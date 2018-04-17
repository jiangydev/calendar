#encoding: utf-8

from exts import db
import shortuuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import enum

'''
task完成状态枚举类
'''
class TaskStatusEnum(enum.Enum):
    FINISHED = 1
    UNFINISHED = 0

'''
前台用户数据模型
'''
class FrontUser(db.Model):
    __tablename__ = 'front_user'
    id = db.Column(db.String(1000), primary_key=True, default=shortuuid.uuid)
    telephone = db.Column(db.String(11), nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False)
    _password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), unique=True)
    join_time = db.Column(db.DateTime, default=datetime.now)

    tasks = db.relationship('Task', backref='user')

    def __init__(self, *args, **kwargs):
        if "password" in kwargs:
            # kwargs为字典形式
            self.password = kwargs.get('password')
            kwargs.pop('password')
            super().__init__(*args, **kwargs)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, newpwd):
        self._password = generate_password_hash(newpwd)

    def check_password(self, rawpwd):
        return check_password_hash(self._password, rawpwd)


'''
Task日程模型
'''
class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.String(100), primary_key=True, default=shortuuid.uuid)
    # task名称
    title = db.Column(db.String(30), nullable=False)
    # task详情
    content = db.Column(db.String(100))
    # 全天时间，默认为否
    all_day = db.Column(db.Boolean, default=False)
    # 开始时间，默认为创建时间
    start = db.Column(db.DateTime, default=datetime.now)
    # 结束时间，可以为空，fullcalendar自动设置为开始时间1小时后
    end = db.Column(db.DateTime)
    # 是否邮件提醒，默认提醒
    email_remind = db.Column(db.Boolean, default=True)
    # 是否短信提醒，默认不提醒
    message_remind = db.Column(db.Boolean, default=False)
    # 短信提醒时间
    remindtime = db.Column(db.DateTime, default=datetime.now)
    # task完成状态，
    status = db.Column(db.Enum(TaskStatusEnum), default=TaskStatusEnum.UNFINISHED)
    # 对应用户
    user_id = db.Column(db.String(100), db.ForeignKey('front_user.id'), nullable=False)



