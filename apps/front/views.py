#encoding: utf-8

from flask import (
    Blueprint,
    views,
    render_template,
    request,
    session,
    url_for
)
from utils import restful, safeutils
from exts import yunpian, db
from .forms import SignupForm, SigninForm
from .models import FrontUser
import config

bp = Blueprint('front', __name__)

'''
前端主界面视图
'''
@bp.route('/')
def index():
    return 'this is home page of front'

'''
前台用户注册界面视图
'''
class SignupView(views.MethodView):
    def get(self):
        return_to = request.referrer
        if return_to and return_to != request.url and safeutils.is_safe_url(return_to):
            return render_template('front/front_signup.html', return_to=return_to)
        else:
            return render_template('front/front_signup.html')
    def post(self):
        form = SignupForm(request.form)
        if form.validate():
            telephone = form.telephone.data
            username = form.username.data
            passowrd = form.password1.data
            user = FrontUser(telephone=telephone, username=username, password=passowrd)
            db.session.add(user)
            db.session.commit()
            return restful.success()
        else:
            return restful.params_error(message=form.get_error())

'''
前台用户登录界面
'''
class SigninView(views.MethodView):
    def get(self):
        return_to = request.referrer
        # print('return_to: {}'.format(return_to))
        # return_to为跳转至此页面前的url，其内容会插入到页面中隐藏的span标签中，此处判断保证
        # 1. return_to 不为空或None
        # 2. return_to 不为当前页
        # 3. return_to 不为注册页
        # 4. return_to 为安全url
        if return_to and return_to != request.url and return_to != url_for('front.signup') and safeutils.is_safe_url(return_to):
            return render_template('front/front_signin.html', return_to=return_to)
        else:
            return render_template('front/front_signin.html')

    def post(self):
        form = SigninForm(request.form)
        if form.validate():
            telephone = form.telephone.data
            password = form.password.data
            remember = form.remember.data
            user = FrontUser.query.filter_by(telephone=telephone).first()
            if user and user.check_password(password):
                session[config.FRONT_USER_ID]  = user.id
                if remember:
                    session.permanent = True
                return restful.success()
            else:
                return restful.params_error(message='手机号或密码错误')
        else:
            return restful.params_error(message=form.get_error())


bp.add_url_rule('/signup/', view_func=SignupView.as_view('signup'))
bp.add_url_rule('/signin/', view_func=SigninView.as_view('signin'))