"""
快速修复脚本：为现有数据库添加班级字段
支持 SQLite 和 MySQL
"""
import sqlite3
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_sqlite_database():
    """修复 SQLite 数据库"""
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'bs_system.db')
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    print(f"📦 找到 SQLite 数据库: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查 users 表是否有 class_id 字段
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'class_id' not in columns:
            print("📝 添加 class_id 字段到 users 表...")
            cursor.execute("ALTER TABLE users ADD COLUMN class_id INTEGER")
            print("✅ class_id 字段已添加")
        else:
            print("ℹ️  class_id 字段已存在")
        
        # 检查是否有 classrooms 表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='classrooms'")
        if not cursor.fetchone():
            print("📝 创建 classrooms 表...")
            cursor.execute("""
                CREATE TABLE classrooms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    description TEXT,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_classrooms_name ON classrooms(name)")
            print("✅ classrooms 表已创建")
        else:
            print("ℹ️  classrooms 表已存在")
        
        # 检查是否有 class_id 索引
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='ix_users_class_id'")
        if not cursor.fetchone():
            print("📝 创建 class_id 索引...")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_users_class_id ON users(class_id)")
            print("✅ class_id 索引已创建")
        else:
            print("ℹ️  class_id 索引已存在")
        
        conn.commit()
        conn.close()
        
        print("\n✅ SQLite 数据库修复完成！")
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def fix_mysql_database():
    """修复 MySQL 数据库"""
    try:
        import pymysql
        from dotenv import load_dotenv
        
        # 加载环境变量
        env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path)
        
        db_host = os.environ.get('DB_HOST', 'localhost')
        db_port = int(os.environ.get('DB_PORT', 3306))
        db_user = os.environ.get('DB_USER', 'bs_user')
        db_password = os.environ.get('DB_PASSWORD', 'password')
        db_name = os.environ.get('DB_NAME', 'bs_system')
        
        print(f"📦 连接 MySQL 数据库: {db_host}:{db_port}/{db_name}")
        
        conn = pymysql.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name,
            charset='utf8mb4'
        )
        
        cursor = conn.cursor()
        
        # 检查 users 表是否有 class_id 字段
        cursor.execute("SHOW COLUMNS FROM users LIKE 'class_id'")
        if not cursor.fetchone():
            print("📝 添加 class_id 字段到 users 表...")
            cursor.execute("ALTER TABLE users ADD COLUMN class_id INT NULL")
            cursor.execute("ALTER TABLE users ADD INDEX ix_users_class_id (class_id)")
            print("✅ class_id 字段已添加")
        else:
            print("ℹ️  class_id 字段已存在")
        
        # 检查是否有 classrooms 表
        cursor.execute("SHOW TABLES LIKE 'classrooms'")
        if not cursor.fetchone():
            print("📝 创建 classrooms 表...")
            cursor.execute("""
                CREATE TABLE classrooms (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    description TEXT,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    INDEX ix_classrooms_name (name)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ classrooms 表已创建")
        else:
            print("ℹ️  classrooms 表已存在")
        
        # 添加外键约束（如果不存在）
        cursor.execute("""
            SELECT CONSTRAINT_NAME 
            FROM information_schema.KEY_COLUMN_USAGE 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'users' 
            AND COLUMN_NAME = 'class_id' 
            AND CONSTRAINT_NAME LIKE 'fk_%'
        """, (db_name,))
        
        if not cursor.fetchone():
            print("📝 添加外键约束...")
            cursor.execute("""
                ALTER TABLE users 
                ADD CONSTRAINT fk_users_class_id 
                FOREIGN KEY (class_id) REFERENCES classrooms(id)
            """)
            print("✅ 外键约束已添加")
        else:
            print("ℹ️  外键约束已存在")
        
        conn.commit()
        conn.close()
        
        print("\n✅ MySQL 数据库修复完成！")
        return True
        
    except ImportError:
        print("⚠️  PyMySQL 未安装，跳过 MySQL 修复")
        return False
    except Exception as e:
        print(f"❌ MySQL 修复失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("🔧 数据库结构修复工具")
    print("=" * 60)
    
    # 检查环境变量
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_path):
        from dotenv import load_dotenv
        load_dotenv(env_path)
    
    db_type = os.environ.get('DB_TYPE', 'sqlite')
    
    if db_type == 'mysql':
        success = fix_mysql_database()
    else:
        success = fix_sqlite_database()
    
    if success:
        print("\n✅ 修复完成！现在可以重新登录系统了。")
        sys.exit(0)
    else:
        print("\n❌ 修复失败，请检查错误信息。")
        sys.exit(1)
