#encoding: utf-8
'''
AJAX返回数据接口：
    必须有code, message, data3项，内容可变。
    返回状态码：
        1. 200：成功
        2. 401：没有授权
        3. 400：参数错误
        4. 500：服务器内部错误
'''

from flask import jsonify

class HttpCode(object):
    ok = 200
    unautherror = 401
    parmserror = 400
    servererror = 500

def resuful_result(code, message, data):
    return jsonify({"code":code, "message":message, "data":data or {}})

def success(message="", data=None):
    return resuful_result(code=HttpCode.ok, message=message, data=data)

def unauth_error(message=""):
    return resuful_result(code=HttpCode.unautherror, message=message, data=None)

def params_error(message=""):
    return resuful_result(code=HttpCode.parmserror, message=message, data=None)

def server_error(message=""):
    return resuful_result(code=HttpCode.servererror, message=message or '服务器内部错误', data=None)