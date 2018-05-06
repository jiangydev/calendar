#encoding: utf-8

from flask import session, redirect, url_for, g
from functools import wraps
import config

'''
登录验证
    如果没有登录，重定向到登录界面
'''
def login_required(func):

    @wraps(func)
    def inner(*args, **kwargs):
        if config.FRONT_USER_ID in session:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('front.signin'))
    return inner
