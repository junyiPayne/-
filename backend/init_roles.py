from app import create_app, db
from app.models.role import Role

app = create_app()

def init_roles():
    with app.app_context():
        roles = [
            {'code': 'admin', 'name': '系统管理员', 'description': '系统管理员，拥有所有权限'},
            {'code': 'teacher', 'name': '教师', 'description': '教师，管理课程和学生'},
            {'code': 'student', 'name': '学生', 'description': '学生，查看课程和提交作业'},
            {'code': 'user', 'name': '普通用户', 'description': '普通注册用户'}
        ]
        
        for r in roles:
            role = Role.query.filter_by(code=r['code']).first()
            if not role:
                role = Role(code=r['code'], name=r['name'], description=r['description'])
                db.session.add(role)
                print(f"Created role: {r['name']}")
            else:
                print(f"Role exists: {r['name']}")
        
        db.session.commit()
        print("Roles initialization completed.")

if __name__ == '__main__':
    init_roles()
