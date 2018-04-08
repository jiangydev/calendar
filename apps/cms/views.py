#encoding: utf-8

from flask import (
    Blueprint
)

bp = Blueprint('cms', __name__, url_prefix='/cms')

'''
cms主界面视图
'''
@bp.route('/')
def index():
    return 'this is home page of cms'