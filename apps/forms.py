#encoding: utf-8

'''
此文件用于存放自定义的表单类，在wtforms.Form类的基础上进行修改，使其更方便于本项目的调用
'''
from wtforms import Form

class BaseForm(Form):
    def get_error(self):
        '''
        虽然可能有多条错误信息，但只显示一条

        :return: str, 出现的错误信息中的一条
        '''
        # print(form.errors)
        # {'password': ['密码长度为6~20位', '其他错误']}
        # popitem返回元组
        return self.errors.popitem()[1][0]

    '''
    重写validate方法，在内部调用父类中方法
    防止报错：signature of method 'MSMCaptchaForm.validate()' does not match signature of base method in class 'BaseForm' less... (Ctrl+F1) 
This inspection detects inconsistencies in overriding method signatures.
    '''
    def validate(self):
        return super().validate()