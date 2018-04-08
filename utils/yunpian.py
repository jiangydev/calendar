#encoding: utf-8
import logging
import requests

'''
***云片网单条短信发送API封装***
云片网短信请求接口重要参数：
    APIKEY  [String] 用户注册获得的唯一标识，在管理控制台获取，需要在配置文件中填写
    mobile  [String] 接收的手机号，仅支持单号码发送 e.g. 15205201314
    text    [String] 已审核短信模板 e.g. 【云片网】您的验证码是1234
可以调用的方法：
    1)send_captcha(self, telephone, captcha, minutes=10)
        **用于发送验证码
        调用的模板为'【日程网】您的验证码为{captcha}， {minutes}分钟内有效。'
        参数：
            telephone：发送短信的目标手机号码
            captcha: 验证码
            minute: 有效时间(分钟)，默认为10分钟，计时功能需要调用者自己完成
返回值：
    返回一个对象，格式为{'code': code, 'message': message},
    其中code取值如下：
        0：发送成功
        1：云片服务器因某些原因拒绝请求，短信发送失败
        2：因为程序逻辑或网络问题，没有接收到预期的相依，短信发送失败
    message内容如下：
        code == 0, message = 'success'
        code == 1, message = '短信发送出问题了'
        code == 2, message = '服务器后台发生了错误'
'''

class YunpianAPI(object):

    # 传入app后，通过APIKEY中的字段查找config中配置
    APIKEY = 'YUNPIAN_APIKEY'

    def __init__(self, app=None):
        self.url = 'https://sms.yunpian.com/v2/sms/single_send.json'
        self.headers = {
            'Accept': 'application/json;charset=utf-8;',
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8;'
        }
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        config = app.config
        try:
            self.apikey = config[self.APIKEY]
        except Exception as e:
            logging.error(e.args)
            raise ValueError('云片短信服务配置错误')

    '''
    对应模板：
        【日程网】您的验证码为#captcha#， #minutes#分钟内有效。
    '''
    def send_captcha(self, telephone, captcha, minutes=10):
        self.sms_text = '【日程网】您的验证码为{captcha}， {minutes}分钟内有效。'.format(captcha=captcha, minutes=minutes)
        self.captcha_params = {
            'apikey': self.apikey,
            'mobile': telephone,
            'text': self.sms_text
        }

        resp = requests.post(self.url, data=self.captcha_params, headers=self.headers)
        data = resp.json()
        print('云片相应信息：{}'.format(data))
        try:
            resultCode = data['code']
            if resultCode == 0:
                return {'code': resultCode, 'message': 'success'}   # 发送成功
            else:
                return {'code': 1, 'message': '短信发送出问题了'}    # 发送失败
        except:
            print("云片短信错误信息： ", data)
            return {'code': 2, 'message': '服务器后台发生了错误'}    # 发送流程出现错误



