#encoding: utf-8

from flask import Blueprint, request, make_response
from exts import yunpian
from utils import restful, zlcache
from utils.captcha import Captcha
from .forms import SMSCaptchaForm
from io import BytesIO


bp = Blueprint('common', __name__, url_prefix='/c')

'''
验证码短信发送接口
通过post请求发送以下参数：
    telephone: 手机号码
    timestamp: 时间戳
    sign：md5加密后得到值
'''
@bp.route('/sms_captcha/', methods=['POST'])
def sms_captcha():
    form = SMSCaptchaForm(request.form)
    if form.validate():
        telephone = form.telephone.data

        # 获取4为随机内容，范围为a-z, A-Z, 0-9
        captcha = Captcha.gene_text(number=4)
        # 发送短信
        result = yunpian.send_captcha(telephone, captcha=captcha)
        if result['code']==0:
            zlcache.set(telephone, captcha, 600) # 存入memcache中
            return restful.success()
        elif result['code'] == 1:
            return restful.params_error(message=result['message'])
        else:
            return restful.params_error(message='服务器离家出走了，请稍后再试')
    else:
        return restful.params_error(message='参数错误')


'''
获取图形验证码接口
'''
@bp.route('/captcha/')
def graph_captcha():
    # 获取验证码
    text, image = Captcha.gene_graph_captcha()
    zlcache.set(text.lower(), text.lower())
    # BytesIO: 自截留
    out = BytesIO()
    image.save(out, 'png')
    out.seek(0) # 将指针返回开头，save过后指针位置在最后
    resp = make_response(out.read())
    resp.content_type = 'image/png'
    return resp