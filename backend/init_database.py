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
            roles[r_cfg['code']] = role
        
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
            admin_user.role_id = roles['admin'].id
            db.session.add(admin_user)
            db.session.commit()
            print("✅ 创建管理员账户: admin / admin123")
        else:
            print("ℹ️  管理员账户已存在")
        
        print("\n✅ 数据库初始化完成！")

if __name__ == '__main__':
    init_database()

