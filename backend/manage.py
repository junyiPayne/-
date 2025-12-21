from flask.cli import FlaskGroup
from app import create_app, db
from app.models import User, Role, Permission
import bcrypt

app = create_app()
cli = FlaskGroup(app)

@cli.command()
def init_db():
    """初始化数据库"""
    db.create_all()
    print("数据库初始化完成")

@cli.command()
def init_admin():
    """创建管理员账户"""
    # 创建管理员角色
    admin_role = Role.query.filter_by(code='admin').first()
    if not admin_role:
        admin_role = Role(
            name='管理员',
            code='admin',
            description='系统管理员'
        )
        db.session.add(admin_role)
        db.session.flush()
    
    # 创建普通用户角色
    user_role = Role.query.filter_by(code='user').first()
    if not user_role:
        user_role = Role(
            name='普通用户',
            code='user',
            description='普通用户'
        )
        db.session.add(user_role)
        db.session.flush()
    
    # 创建管理员用户
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
        print(f"创建管理员账户: admin / admin123")
    else:
        print("管理员账户已存在")
    
    db.session.commit()
    print("初始化完成")

@cli.command()
def runserver():
    """运行开发服务器"""
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    cli()

