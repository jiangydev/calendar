#encoding: utf-8

from apps.forms import BaseForm
from wtforms import StringField
from wtforms.validators import  regexp, InputRequired
import hashlib

class SMSCaptchaForm(BaseForm):
    salt = 'hfjkasdhiasd;hjiopjcid'
    telephone = StringField(validators=[regexp(r'1[135789]\d{9}')])
    timestamp = StringField(validators=[regexp(r'\d{13}')])
    sign = StringField(validators=[InputRequired()])

    def validate(self):
        result = super().validate()
        if not result:  # 原生验证没有通过
            return False
        telephone = self.telephone.data
        timestamp = self.timestamp.data
        sign = self.sign.data

        # md5(timestamp + telephon + salt)
        # md5函数不需要传一个bytes类型的字符串进去
        # hexdigest获取md5序列字符串
        sign2 = hashlib.md5((timestamp+telephone+self.salt).encode('utf-8')).hexdigest()
        if sign == sign2:
            return True
        else:
            return False
