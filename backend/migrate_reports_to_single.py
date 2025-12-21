"""
迁移报告表：每个用户只有一个报告，添加修改日志
1. 为user_id添加unique约束
2. 添加updated_at字段
3. 创建report_history表
4. 迁移现有数据（如果有多个报告，只保留最新的）
"""
from app import create_app, db
from sqlalchemy import text, inspect
from app.models.report import Report, ReportHistory
from app.models.user import User
from datetime import datetime, timezone

app = create_app()

def migrate_reports():
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            db_url = str(db.engine.url)
            is_sqlite = 'sqlite' in db_url.lower()
            
            # 1. 先添加updated_at字段（如果不存在），避免查询时出错
            print("检查updated_at字段...")
            columns = [col['name'] for col in inspector.get_columns('reports')]
            if 'updated_at' not in columns:
                if is_sqlite:
                    # SQLite不支持ALTER TABLE ADD COLUMN with default，需要特殊处理
                    print("SQLite数据库，添加updated_at字段...")
                    # 先添加列（SQLite支持ADD COLUMN）
                    db.session.execute(text('ALTER TABLE reports ADD COLUMN updated_at DATETIME'))
                    # 更新现有记录的updated_at为created_at
                    db.session.execute(text('UPDATE reports SET updated_at = created_at WHERE updated_at IS NULL'))
                else:
                    db.session.execute(text('ALTER TABLE reports ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
                db.session.commit()
                print("已添加updated_at字段")
            else:
                print("updated_at字段已存在")
            
            # 2. 检查并处理重复报告（保留最新的）
            print("检查重复报告...")
            # 使用原始SQL查询避免模型字段不匹配的问题
            result = db.session.execute(text('SELECT id, user_id, created_at FROM reports ORDER BY user_id, created_at DESC'))
            reports_data = result.fetchall()
            
            reports_to_keep = {}
            reports_to_delete = []
            
            for row in reports_data:
                report_id, user_id, created_at = row
                if user_id not in reports_to_keep:
                    reports_to_keep[user_id] = (report_id, created_at)
                else:
                    # 保留创建时间最新的
                    existing_id, existing_created_at = reports_to_keep[user_id]
                    if created_at > existing_created_at:
                        # 删除旧的
                        reports_to_delete.append(existing_id)
                        reports_to_keep[user_id] = (report_id, created_at)
                    else:
                        # 删除当前的
                        reports_to_delete.append(report_id)
            
            if reports_to_delete:
                print(f"删除 {len(reports_to_delete)} 个重复报告...")
                for report_id in reports_to_delete:
                    db.session.execute(text('DELETE FROM reports WHERE id = :id'), {'id': report_id})
                db.session.commit()
                print(f"已清理重复报告，每个用户保留一个报告")
            else:
                print("没有重复报告需要清理")
            
            # 3. 创建report_history表
            print("检查report_history表...")
            if 'report_history' not in inspector.get_table_names():
                print("创建report_history表...")
                db.create_all()  # 这会创建所有缺失的表
                print("已创建report_history表")
            else:
                print("report_history表已存在")
            
            # 4. 为user_id添加unique约束（SQLite需要重建表）
            print("检查user_id唯一约束...")
            # 获取索引信息
            indexes = inspector.get_indexes('reports')
            has_unique_user_id = any(
                idx['unique'] and 'user_id' in str(idx.get('column_names', []))
                for idx in indexes
            )
            
            if not has_unique_user_id:
                if is_sqlite:
                    print("SQLite数据库，需要重建表以添加unique约束...")
                    # SQLite不支持直接添加unique约束，需要重建表
                    db.session.execute(text('''
                        CREATE TABLE reports_new (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL UNIQUE,
                            title VARCHAR(200) NOT NULL,
                            file_path VARCHAR(255),
                            pdf_content BLOB,
                            status VARCHAR(20) DEFAULT 'submitted',
                            created_at DATETIME,
                            updated_at DATETIME,
                            FOREIGN KEY(user_id) REFERENCES users(id)
                        )
                    '''))
                    
                    # 复制数据
                    db.session.execute(text('''
                        INSERT INTO reports_new (id, user_id, title, file_path, pdf_content, status, created_at, updated_at)
                        SELECT id, user_id, title, file_path, pdf_content, status, created_at, updated_at
                        FROM reports
                    '''))
                    
                    # 删除旧表
                    db.session.execute(text('DROP TABLE reports'))
                    
                    # 重命名新表
                    db.session.execute(text('ALTER TABLE reports_new RENAME TO reports'))
                    
                    db.session.commit()
                    print("已重建reports表，添加了user_id唯一约束")
                else:
                    # MySQL等支持直接添加unique约束
                    db.session.execute(text('ALTER TABLE reports ADD UNIQUE KEY unique_user_id (user_id)'))
                    db.session.commit()
                    print("已添加user_id唯一约束")
            else:
                print("user_id唯一约束已存在")
            
            # 5. 为现有报告创建初始历史记录
            print("为现有报告创建初始历史记录...")
            # 使用SQL查询获取所有报告ID和user_id
            result = db.session.execute(text('SELECT id, user_id FROM reports'))
            reports_data = result.fetchall()
            
            for report_id, user_id in reports_data:
                # 检查是否已有历史记录
                existing_history = db.session.execute(
                    text('SELECT id FROM report_history WHERE report_id = :report_id LIMIT 1'),
                    {'report_id': report_id}
                ).fetchone()
                
                if not existing_history:
                    db.session.execute(
                        text('''
                            INSERT INTO report_history (report_id, modified_by_id, action, description, created_at)
                            VALUES (:report_id, :modified_by_id, :action, :description, :created_at)
                        '''),
                        {
                            'report_id': report_id,
                            'modified_by_id': user_id,
                            'action': 'created',
                            'description': '报告创建',
                            'created_at': datetime.now(timezone.utc)
                        }
                    )
            
            db.session.commit()
            print(f"已为 {len(reports_data)} 个报告创建初始历史记录")
            
            print("\n✅ 报告表迁移完成！")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ 迁移失败: {e}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == '__main__':
    migrate_reports()

