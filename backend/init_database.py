"""数据库初始化脚本"""
from app import create_app, db
from app.models import User, Role, UserProfile, DailyLog, BusinessData

def init_database():
    """初始化数据库"""
    app = create_app()
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("✅ 数据库表创建完成")
        
        # 创建角色
        admin_role = Role.query.filter_by(code='admin').first()
        if not admin_role:
            admin_role = Role(
                name='管理员',
                code='admin',
                description='系统管理员'
            )
            db.session.add(admin_role)
            print("✅ 创建管理员角色")
        
        user_role = Role.query.filter_by(code='user').first()
        if not user_role:
            user_role = Role(
                name='普通用户',
                code='user',
                description='普通用户'
            )
            db.session.add(user_role)
            print("✅ 创建普通用户角色")
        
        db.session.commit()
        
        # 创建管理员账户
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                real_name='系统管理员'
            )
            admin_user.set_password('admin123')
            admin_user.role_id = admin_role.id
            db.session.add(admin_user)
            db.session.commit()
            print("✅ 创建管理员账户: admin / admin123")
        else:
            print("ℹ️  管理员账户已存在")
        
        print("\n✅ 数据库初始化完成！")

if __name__ == '__main__':
    init_database()

