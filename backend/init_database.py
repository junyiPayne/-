"""数据库初始化脚本"""
from app import create_app, db
from app.models import User, Role, UserProfile, DailyLog, BusinessData, Classroom, SystemSetting, UserSettings
import os
import shutil
import glob
from datetime import datetime

def find_latest_backup(backup_dir):
    """查找最新的备份文件"""
    if not os.path.exists(backup_dir):
        return None
    
    # 查找所有备份文件
    backup_pattern = os.path.join(backup_dir, 'bs_system_backup_*.db')
    backups = glob.glob(backup_pattern)
    
    if not backups:
        return None
    
    # 按修改时间排序，返回最新的
    backups.sort(key=os.path.getmtime, reverse=True)
    return backups[0]

def restore_from_backup(backup_path, target_path):
    """从备份恢复数据库"""
    try:
        # 确保目标目录存在
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        # 复制备份文件
        shutil.copy2(backup_path, target_path)
        print(f"✅ 已从备份恢复数据库: {backup_path} -> {target_path}")
        return True
    except Exception as e:
        print(f"❌ 恢复备份失败: {e}")
        return False

def init_database():
    """初始化数据库 - 自动检测并处理数据库创建和初始化"""
    app = create_app()
    
    # 确保instance目录存在
    instance_path = app.instance_path
    os.makedirs(instance_path, exist_ok=True)
    
    # 打印数据库信息用于调试
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    print(f"数据库URI: {db_uri}")
    print(f"Instance路径: {instance_path}")
    
    # 判断数据库类型
    is_sqlite = db_uri.startswith('sqlite:///')
    is_mysql = 'mysql' in db_uri.lower() or 'pymysql' in db_uri.lower()
    
    if is_sqlite:
        print("📦 数据库类型: SQLite")
        db_path = db_uri.replace('sqlite:///', '')
        
        # 如果路径不是绝对路径，转换为绝对路径
        if not os.path.isabs(db_path):
            if 'instance/' in db_path or 'instance\\' in db_path:
                db_filename = os.path.basename(db_path)
            else:
                db_filename = db_path
            db_path = os.path.abspath(os.path.join(instance_path, db_filename))
            app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
            print(f"✅ 已转换为绝对路径: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # 检查数据库文件是否已存在
        if os.path.exists(db_path):
            # 检查文件大小，如果太小可能是损坏的
            file_size = os.path.getsize(db_path)
            if file_size > 1024:  # 至少1KB
                print(f"✅ 发现已有数据库文件: {db_path} (大小: {file_size} 字节)")
                print("ℹ️  将使用现有数据库，不会重新初始化")
            else:
                print(f"⚠️  数据库文件存在但可能损坏（大小: {file_size} 字节），尝试恢复备份")
                db_path = None  # 标记为需要恢复
        else:
            print(f"ℹ️  数据库文件不存在: {db_path}")
            print("🔍 正在查找备份文件...")
            
            # 查找备份目录
            backup_dir = os.path.join(os.getcwd(), 'backups')
            if not os.path.exists(backup_dir):
                # 尝试在项目根目录查找
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                backup_dir = os.path.join(project_root, 'backups')
            
            latest_backup = find_latest_backup(backup_dir)
            
            if latest_backup:
                print(f"✅ 找到最新备份: {latest_backup}")
                backup_time = datetime.fromtimestamp(os.path.getmtime(latest_backup))
                print(f"   备份时间: {backup_time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # 询问是否恢复（自动恢复）
                print("🔄 正在从备份恢复数据库...")
                if restore_from_backup(latest_backup, db_path):
                    print("✅ 数据库恢复成功！")
                else:
                    print("❌ 恢复失败，将创建新数据库")
                    db_path = None
            else:
                print("ℹ️  未找到备份文件，将创建新数据库")
                db_path = None
        
        # 如果数据库不存在，创建新数据库
        if db_path is None or not os.path.exists(db_path):
            print("🆕 创建新数据库...")
            # 确保目录存在
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            # 创建空数据库文件
            try:
                import sqlite3
                conn = sqlite3.connect(db_path)
                conn.close()
                print(f"✅ 已创建数据库文件: {db_path}")
            except Exception as e:
                print(f"❌ 创建数据库文件失败: {e}")
                return
        
        # 验证最终路径
        final_db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        db_dir = os.path.dirname(final_db_path)
        print(f"数据库目录: {db_dir}")
        print(f"目录存在: {os.path.exists(db_dir)}")
        print(f"目录可写: {os.access(db_dir, os.W_OK) if os.path.exists(db_dir) else False}")
        
        # 验证数据库文件
        if os.path.exists(final_db_path):
            file_size = os.path.getsize(final_db_path)
            print(f"数据库文件大小: {file_size} 字节")
    
    elif is_mysql:
        print("📦 数据库类型: MySQL")
        print("ℹ️  注意: MySQL 主要用于 Docker 生产环境，本地开发建议使用 SQLite")
        print("🔍 检查数据库状态...")
        
        # 尝试连接数据库并检查是否存在
        with app.app_context():
            try:
                from sqlalchemy import inspect, text, create_engine
                from sqlalchemy.exc import OperationalError
                
                # 先尝试连接数据库
                try:
                    # 测试连接
                    db.session.execute(text("SELECT 1"))
                    print("✅ 数据库连接成功")
                except OperationalError as e:
                    error_msg = str(e)
                    print(f"⚠️  数据库连接失败: {error_msg}")
                    
                    # 检查是否是数据库不存在的问题
                    if "Unknown database" in error_msg or "1049" in error_msg:
                        print("ℹ️  数据库不存在，尝试自动创建...")
                        
                        # 尝试创建数据库
                        try:
                            # 从连接字符串中提取数据库名称
                            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
                            # 解析数据库名称（格式：mysql+pymysql://user:pass@host:port/dbname）
                            db_name = db_uri.split('/')[-1].split('?')[0]
                            
                            # 创建不包含数据库名的连接（连接到 MySQL 服务器）
                            # 提取基础连接信息
                            if '@' in db_uri:
                                base_uri = db_uri.rsplit('/', 1)[0]  # 移除数据库名
                                # 连接到 MySQL 服务器（不指定数据库）
                                server_engine = create_engine(base_uri)
                                
                                with server_engine.connect() as conn:
                                    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                                    conn.commit()
                                
                                print(f"✅ 已创建数据库: {db_name}")
                                
                                # 关闭旧连接，重新连接数据库
                                db.session.close()
                                db.engine.dispose()
                                # 重新连接（SQLAlchemy 会自动使用新的连接）
                                db.session.execute(text("SELECT 1"))
                                print("✅ 数据库连接成功")
                            else:
                                raise Exception("无法解析数据库连接字符串")
                        except Exception as create_error:
                            print(f"❌ 自动创建数据库失败: {create_error}")
                            print("   请手动创建数据库:")
                            print(f"   CREATE DATABASE `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
                            raise
                    elif "Access denied" in error_msg or "1045" in error_msg:
                        print("⚠️  数据库访问被拒绝，请检查用户名和密码")
                        raise
                    elif "Can't connect" in error_msg or "2003" in error_msg:
                        print("⚠️  无法连接到 MySQL 服务器，请检查:")
                        print("   1. MySQL 服务是否运行")
                        print("   2. DB_HOST 配置是否正确（本地应为 localhost）")
                        print("   3. MySQL 端口是否正确（默认 3306）")
                        raise
                    else:
                        raise
                
                # 检查数据库是否存在（通过检查表）
                inspector = inspect(db.engine)
                existing_tables = inspector.get_table_names()
                
                if existing_tables:
                    print(f"✅ 发现已有数据库，包含 {len(existing_tables)} 个表")
                    print(f"   现有表: {', '.join(existing_tables[:5])}{'...' if len(existing_tables) > 5 else ''}")
                    print("ℹ️  将使用现有数据库，只创建缺失的表和数据")
                else:
                    print("ℹ️  数据库存在但为空，将创建新表")
            except Exception as e:
                print(f"⚠️  检查数据库时出错: {e}")
                print("ℹ️  将尝试继续初始化，如果失败请检查 MySQL 配置")
    else:
        print(f"⚠️  未知的数据库类型: {db_uri}")
    
    with app.app_context():
        # 检查数据库是否已有表（判断是否已初始化）
        from sqlalchemy import inspect, text
        from sqlalchemy.exc import OperationalError
        try:
            # 先测试连接
            db.session.execute(text("SELECT 1"))
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            # 检查关键表是否存在
            required_tables = ['users', 'roles', 'system_settings', 'user_settings']
            missing_tables = [t for t in required_tables if t not in existing_tables]
            
            if existing_tables and len(existing_tables) > 0:
                # 数据库已存在且有表
                print(f"📊 数据库状态: 已有数据库，包含 {len(existing_tables)} 个表")
                if missing_tables:
                    print(f"⚠️  缺少关键表: {', '.join(missing_tables)}")
                    print("📦 创建缺失的表...")
                    db.create_all()
                    print("✅ 缺失的表已创建")
                else:
                    print("✅ 所有关键表已存在")
                    # 确保所有表都存在（包括新添加的表，但不影响现有数据）
                    db.create_all()
                    print("✅ 数据库表结构已更新（如有新表）")
            else:
                # 数据库不存在或为空，创建新数据库
                print("🆕 数据库为空或不存在，创建新数据库和表...")
                db.create_all()
                print("✅ 数据库表创建完成")
        except Exception as e:
            print(f"⚠️  检查表时出错: {e}")
            print("📦 尝试创建所有表...")
            try:
                db.create_all()
                print("✅ 数据库表创建完成")
            except Exception as create_error:
                print(f"❌ 创建表失败: {create_error}")
                raise
        
        # 创建角色（如果不存在）
        roles_config = [
            {'code': 'admin', 'name': '管理员', 'description': '系统管理员'},
            {'code': 'teacher', 'name': '教师', 'description': '教师，管理课程和学生'},
            {'code': 'student', 'name': '学生', 'description': '学生，查看课程和提交作业'},
            {'code': 'user', 'name': '普通用户', 'description': '普通注册用户'}
        ]
        
        roles = {}
        for r_cfg in roles_config:
            role = Role.query.filter_by(code=r_cfg['code']).first()
            if not role:
                role = Role(
                    name=r_cfg['name'],
                    code=r_cfg['code'],
                    description=r_cfg['description']
                )
                db.session.add(role)
                print(f"✅ 创建{r_cfg['name']}角色")
            else:
                print(f"ℹ️  {r_cfg['name']}角色已存在")
            roles[r_cfg['code']] = role
        
        db.session.commit()
        
        # 创建管理员账户（如果不存在）
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                real_name='系统管理员'
            )
            admin_user.set_password('admin123')
            admin_user.role_id = roles['admin'].id
            db.session.add(admin_user)
            db.session.commit()
            print("✅ 创建管理员账户: admin / admin123")
        else:
            print("ℹ️  管理员账户已存在")
        
        # 初始化系统设置（如果不存在）
        maintenance_setting = SystemSetting.query.filter_by(key='maintenance_mode').first()
        if not maintenance_setting:
            maintenance_setting = SystemSetting(
                key='maintenance_mode',
                value='false',
                description='系统维护模式开关'
            )
            db.session.add(maintenance_setting)
            db.session.commit()
            print("✅ 初始化系统设置: maintenance_mode")
        else:
            print("ℹ️  系统设置已存在")
        
        print("\n✅ 数据库初始化完成！")

if __name__ == '__main__':
    init_database()

