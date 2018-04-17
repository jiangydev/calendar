#encoding: utf-8

from flask import (
    Blueprint,
    views,
    render_template,
    request,
    session,
    url_for,
    g,
    jsonify
)
from utils import restful, safeutils
from exts import db
from .forms import SignupForm, SigninForm, NewtaskForm, ModifyTaskForm, DelTaskForm
from .models import FrontUser, Task
import config
from datetime import datetime


bp = Blueprint('front', __name__)

@bp.route('/helloworld/')
def helloworld():
    return 'hello world'

'''
前端主界面视图
'''
@bp.route('/')
def index():
    return render_template('front/front_index.html')

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

'''
新建日程接口
'''
@bp.route('/newtask/', methods=['POST'])
def newtask():
    form = NewtaskForm(request.form)
    if form.validate():
        task_args = form.getTrueValue()

        task = Task(**task_args)
        db.session.add(task)
        db.session.commit()

        return restful.success()
    else:
        return restful.params_error(message=form.get_error())


'''
修改日程接口
'''
@bp.route('/modtask/', methods=['POST'])
def modtask():
    form = ModifyTaskForm(request.form)
    if form.validate():
        task_args = form.getTrueValue()
        task_id = form.task_id.data
        task = Task.query.filter_by(id=task_id).first()
        if task:
            task.title = task_args['title']
            task.content = task_args['content']
            task.all_day = task_args['all_day']
            task.start = task_args['start']
            task.end = task_args['end']
            task.email_remind = task_args['email_remind']
            task.message_remind = task_args['message_remind']
            task.remindtime = task_args['remindtime']
            task.status = task_args['status']
            db.session.commit()
            return restful.success()
        else:
            return restful.params_error(message='该日程不存在')
    else:
        return restful.params_error(message=form.get_error())

@bp.route('/deltask/', methods=['POST'])
def deltask():
    form = DelTaskForm(request.form)
    if form.validate():
        task_id = form.task_id.data
        task = Task.query.get(task_id)
        if task:
            db.session.delete(task)
            db.session.commit()
            return restful.success()
        else:
            return restful.params_error(message="此日程并未创建")
    else:
        return restful.params_error(message="日程id错误")

'''
查询日程接口
    返回当前用户的所有日程
    返回格式：JSON, { 'code': xxx, 'data':[...] }
        code意义：200 - 成功
                  500 - 出错 
'''
@bp.route('/tasks/')
def tasks():
    user = g.front_user
    tasks =[]

    def datetime2iso(dateobj):
        '''
        :param dateobj: datetime.datetime或其他类型
        :return: 如果dateobj为datetime.datetime，则返回其转换为ISO 8601后字符串；否则返回''
        '''
        if isinstance(dateobj, datetime):
            return dateobj.isoformat()
        else:
            return ''

    try:
        for task in user.tasks:
            tasks.append({
                'id': task.id,
                'title': task.title,
                'content': task.content,
                'all_day': task.all_day,
                'start': datetime2iso(task.start),
                'end': datetime2iso(task.end),
                'email_remind': task.email_remind,
                'message_remind': task.message_remind,
                'remindtime': datetime2iso(task.remindtime),
                'status': task.status.value
            })
    except:
        return jsonify({'code': 500, 'data': []})

    return jsonify({'code': 200, 'data': tasks})


bp.add_url_rule('/signup/', view_func=SignupView.as_view('signup'))
bp.add_url_rule('/signin/', view_func=SigninView.as_view('signin'))
