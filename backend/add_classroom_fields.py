"""
数据库迁移脚本：添加班级相关字段
为现有的 users 表添加 class_id 字段，并创建 classrooms 表
"""
from app import create_app, db
from sqlalchemy import text

def migrate_database():
    """迁移数据库，添加班级相关字段"""
    app = create_app()
    
    with app.app_context():
        try:
            # 检查数据库类型
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            is_sqlite = db_uri.startswith('sqlite')
            is_mysql = 'mysql' in db_uri.lower()
            
            print("=" * 60)
            print("🔄 开始数据库迁移：添加班级模块")
            print(f"   数据库类型: {'SQLite' if is_sqlite else 'MySQL' if is_mysql else 'Unknown'}")
            print("=" * 60)
            
            # 检查 classrooms 表是否存在
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            # 创建 classrooms 表（如果不存在）
            if 'classrooms' not in existing_tables:
                print("\n📦 创建 classrooms 表...")
                db.create_all()
                print("✅ classrooms 表创建完成")
            else:
                print("\nℹ️  classrooms 表已存在")
            
            # 检查 users 表是否有 class_id 字段
            if 'users' in existing_tables:
                users_columns = [col['name'] for col in inspector.get_columns('users')]
                
                if 'class_id' not in users_columns:
                    print("\n📦 为 users 表添加 class_id 字段...")
                    
                    if is_sqlite:
                        # SQLite 添加列
                        db.session.execute(text("ALTER TABLE users ADD COLUMN class_id INTEGER"))
                        db.session.execute(text("CREATE INDEX IF NOT EXISTS ix_users_class_id ON users(class_id)"))
                    elif is_mysql:
                        # MySQL 添加列
                        db.session.execute(text("ALTER TABLE users ADD COLUMN class_id INT NULL"))
                        db.session.execute(text("ALTER TABLE users ADD INDEX ix_users_class_id (class_id)"))
                        db.session.execute(text("ALTER TABLE users ADD CONSTRAINT fk_users_class_id FOREIGN KEY (class_id) REFERENCES classrooms(id)"))
                    else:
                        # 使用 SQLAlchemy 的通用方法
                        db.session.execute(text("ALTER TABLE users ADD COLUMN class_id INTEGER"))
                    
                    db.session.commit()
                    print("✅ class_id 字段添加完成")
                else:
                    print("\nℹ️  users 表已包含 class_id 字段")
            else:
                print("\n⚠️  users 表不存在，将创建所有表...")
                db.create_all()
                print("✅ 所有表创建完成")
            
            print("\n" + "=" * 60)
            print("✅ 数据库迁移完成！")
            print("=" * 60)
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ 迁移失败: {e}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == '__main__':
    migrate_database()
