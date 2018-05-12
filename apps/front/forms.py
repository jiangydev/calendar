#encoding: utf-8

from ..forms import BaseForm
from wtforms import StringField
from wtforms.validators import Regexp, EqualTo, ValidationError, Length, InputRequired
from utils import zlcache
from datetime import datetime, timedelta
from flask import g


'''
前台用户注册界面提交按钮表单验证
'''
class SignupForm(BaseForm):
    telephone = StringField(validators=[Regexp(r"1[35789]\d{9}", message='请输入正确格式的手机号码')])
    sms_captcha = StringField(validators=[Regexp(r"\w{4}", message='请输入正确的短信验证码')])
    username = StringField(validators=[Length(2, 20, message='请输入正确格式的用户名')])
    password1 = StringField(validators=[Length(6, 20, message='请输入正确格式的密码')])
    password2 = StringField(validators=[EqualTo('password1', message='两次输入的密码不一致')])
    graph_captcha = StringField(validators=[Regexp(r'\w{4}', message='请输入正确格式的图形验证码')])

    def validate_sms_captcha(self, field):
        sms_captcha = field.data
        # 该判断为测试代码
        # if sms_captcha != '1111':
        telephone = self.telephone.data

        sms_captcha_mem = zlcache.get(telephone)
        if not sms_captcha_mem or sms_captcha_mem.lower() != sms_captcha.lower():
            raise ValidationError(message='短信验证码错误')

    def validate_graph_captcha(self, field):
        graph_captcha = field.data
        # 该判断为测试代码
        # if graph_captcha != '1111':
        graph_captcha_mem = zlcache.get(graph_captcha.lower())
        # print('username: {}'.format(self.username.data))
        # print('password1: {}'.format(self.password1.data))
        # print('password2: {}'.format(self.password2.data))
        # print('telephone: {}'.format(self.telephone.data))
        # print('sms_captcha: {}'.format(self.sms_captcha.data))
        # print('graph_captcha: {}'.format(self.graph_captcha.data))
        if not graph_captcha_mem:
            raise ValidationError(message='图形验证码错误')


'''
前台用户登录界面提交按钮表单验证
'''
class SigninForm(BaseForm):
    # 在Python的string前面加上‘r’， 是为了告诉编译器这个string是个raw string，不要转意backslash '\'
    telephone = StringField(validators=[Regexp(r"1[35789]\d{9}", message='请输入正确格式的手机号码')])
    password = StringField(validators=[Length(6, 20, message='请输入正确格式的密码')])
    remember = StringField()


'''
新建/修改日程表单验证父类
'''
class TaskForm(BaseForm):
    '''
    新建/修改日程表单验证父类
    '''

    # 从验真给前端提交的基本数据
    title = StringField(validators=[Length(0, 15, message='日程名称限15字')])
    content = StringField(validators=[Length(0, 150, message='日程描述限150字')])
    all_day = StringField()
    # 接受时间格式: 2018-04-08 21:00
    start = StringField(validators=[Regexp(r"20\d{2}-\d{2}-\d{2}\s\d{2}:\d{2}", message='请输入开始时间')])
    end = StringField()
    email_remind = StringField()
    message_remind = StringField()
    remindtime = StringField()
    status = StringField()
    # user_id = StringField(validators=[InputRequired()])

    def str2datetime(self, timestr):
        '''
        将接收到的时间子浮窗格式化，并转换成对应时间datetime对象；如果接收的参数不符合要求，则返回空字符串
        参数：
            timestr: 形如‘2018-04-10 19:55’的时间字符串
        返回：
            对应时间的datetime.datetime对象,或空字符串
        '''
        if isinstance(timestr, str) and not timestr == '':
            try:
                return datetime.strptime(timestr, '%Y-%m-%d %H:%M')
            except ValueError:
                return ''
        else:
            return ''

    # 类型转换
    # 将从前端接收的数据验证后装换成数据库需要的类型，放入自定义的类属性
    def typeTran(self):
        self.Ttitle = self.title.data
        self.Tcontent = self.content.data
        self.Tstart = self.str2datetime(self.start.data)
        self.Tend = self.str2datetime(self.end.data)
        self.Tremindtime = self.str2datetime(self.remindtime.data)
        self.Tall_day = True if (self.all_day.data == 'true') else False
        self.Temail_remind = True if (self.email_remind.data == 'true') else False
        self.Tmessage_remind = True if (self.message_remind.data == 'true') else False
        self.Tstatus = 'FINISHED' if (self.status.data == '1') else 'UNFINISHED'

    # 设置默认值
    def setDefault(self):
        '''
        设置结束时间、提醒时间默认值
        如果end（结束时间）没有填写，则默认为开始时间后1小时
        如果remindtime(提醒时间)没有填写，默认为开始时间
        '''
        self.Tend = self.Tend or self.Tstart+timedelta(hours=1)
        self.Tremindtime = self.Tremindtime or self.Tstart

    # 调用实例时获取格式化后数据的方法
    def getTrueValue(self):
        '''
        调用实例时获取格式化后数据的方法
        在接收数据后，进行格式转换和设置默认值，将数据转换成数据库接收的格式，并添加一些功能
        !!! 注意，吃出进提供处理后的数据，并不包括表单验证，实际使用时需调用self.validate()
        :return: dict :: {
            'title': task_content_here
            'content': task_content_here
            'all_day': task_content_here
            'start': task_content_here
            'end': task_content_here
            'email_remind': task_content_here
            'message_remind': task_content_here
            'remindtime': task_content_here
            'status': task_content_here
            'user_id': task_content_here
        }
        '''
        self.typeTran()
        self.setDefault()
        return {
            'title': self.Ttitle,
            'content': self.Tcontent,
            'all_day': self.Tall_day,
            'start': self.Tstart,
            'end': self.Tend,
            'email_remind': self.Temail_remind,
            'message_remind': self.Tmessage_remind,
            'remindtime': self.Tremindtime,
            'status': self.Tstatus,
            'user_id': g.front_user.id
        }

    def __init__(self, *args, **kwargs):
        '''
        初始化函数，调用符类初始化，然后自定义类属性用于存储处理后数据
        :param args: 用于接收父类初始化需要的参数
        :param kwargs: 用于接收父类初始化需要的参数
        '''
        super().__init__(*args, **kwargs)
        self.Ttitle = ''
        self.Tcontent = ''
        self.Tstart = datetime.now()
        self.Tend = datetime.now()
        self.Tremindtime = datetime.now()
        self.Tall_day = True
        self.Temail_remind = True
        self.Tmessage_remind = True
        self.Tstatus = 'FINISHED'

'''
新建日程表单验证
'''
class NewtaskForm(TaskForm):
    pass

'''
修改日程表单验证
'''
class ModifyTaskForm(TaskForm):
    # 修改日程时相比创建日程需要额外接收task_id用于检索日程
    task_id = StringField(validators=[InputRequired()])

'''
删除日程表单验证
'''
class DelTaskForm(BaseForm):
    task_id = StringField(validators=[InputRequired()])


'''
课表设置表单验证
'''
class ClassScheduleForm(BaseForm):
    startDate = StringField(validators=[InputRequired(message="未选择第一周周一日期")])
    studentID = StringField(validators=[Length(9, 9, message='学号格式错误')])
    password = StringField(validators=[InputRequired(message="未输入密码")])
    # classCaptcha = StringField(validators=[Length(4, 4, message='验证码格式错误')])