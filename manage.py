#encoding: utf-8

from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate
from Calendar import create_app
from exts import db
from apps.front import models as front_model

app = create_app()

manager = Manager(app)

Migrate(app, db)
manager.add_command('db', MigrateCommand)

FrontUser = front_model.FrontUser
Task = front_model.Task



# ============ 前台系统 =================
'''
添加前台用户测试
'''
@manager.option('-t', '--telephone', dest='telephone')
@manager.option('-u', '--username', dest='username')
@manager.option('-p', '--password', dest='password')
def create_front_user(telephone, username, password):
    user = FrontUser(telephone=telephone, username=username, password=password)
    db.session.add(user)
    db.session.commit()

'''
添加task测试
'''
@manager.option('-t', '--title', dest='title')
@manager.option('-u', '--username', dest='username')
def create_task(title, username):
    user = FrontUser.query.filter_by(username=username).first()
    if user:
        task = Task(title=title, user_id=user.id)
        db.session.add(task)
        db.session.commit()
    else:
        print('no such user')


if __name__ == '__main__':
    manager.run()
