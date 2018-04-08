#encoding: utf-8

from ..forms import BaseForm
from wtforms import StringField
from wtforms.validators import Regexp, EqualTo, ValidationError, Length
from utils import zlcache

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
