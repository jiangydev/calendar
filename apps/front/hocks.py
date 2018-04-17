#encoding: utf-8

from .views import bp
import config
from flask import session, g
from .models import FrontUser

'''
在请求到达之前确认用户是否登录
如果用户已经登录，就吧用户信息放到g对象中
'''
@bp.before_request
def before_request():
    if config.FRONT_USER_ID in session:
        user_id = session.get(config.FRONT_USER_ID)
        user = FrontUser.query.get(user_id)
        if user:
            g.front_user = user