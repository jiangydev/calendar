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
from utils import restful, safeutils, zlcache
from utils.classUtils import ZhengfangSpider, Lesson
from exts import db, mongo
from .forms import SignupForm, SigninForm, NewtaskForm, ModifyTaskForm, DelTaskForm, ClassScheduleForm
from .models import FrontUser, Task
import config
from datetime import datetime
from .decorators import login_required
from lxml import etree



bp = Blueprint('front', __name__)

@bp.route('/helloworld/')
def helloworld():
    return 'hello world'

'''
前端主界面视图
'''
@bp.route('/')
@login_required
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

'''
个人信息设置页面
'''
@bp.route('/settings/')
@login_required
def settings():
    return render_template('front/front_settings.html')

'''
课表设置接口
'''
class ClassSchedule(views.MethodView):
    decorators = [login_required]
    def get(self):
        pass

    def post(self):
        form = ClassScheduleForm(request.form)
        if form.validate():
            startDate = form.startDate.data
            studentID = form.studentID.data
            password = form.password.data
            # classCaptcha = form.classCaptcha.data
            print(startDate, studentID, password)

            # 爬取内容
            spider = ZhengfangSpider(studentNum=studentID, password=password)
            spider.login()
            page_content = spider.getClassSchedule()


            # 解析并存储
            collection = mongo.db.flask
            user_tel = g.front_user.telephone

            # 构造html解析器
            parser = etree.HTMLParser(encoding='utf-8')
            html = etree.HTML(page_content, parser=parser)

            # 获取课程信息所在td标签
            tds = html.xpath("//tr[position()>2]/td[@align='Center']//text()")
            if len(tds) == 0:
                # raise ValueError('get classSchedule fail')
                return restful.server_error(message='爬取或解析课表过程出错')

            # 取出列表中无用杂项
            for i in range(0, tds.count('\xa0')):
                tds.remove('\xa0')

            # print(tds)

            def saveLessons(times, name):
                '''saveLessons
                获取课程信息，并将其存入mongoDB数据库
                :param times: [list] 课程时间列表，包含一节课的周次、每周周几、一天第几节
                    e.g. ('week1', 'day1', 1)
                :param name: [str] 课程名称，e.g. 机器人视觉@南B309
                :return: result [boolean] True: 保存成功， False: 保存失败
                '''
                for time in times:
                    # time : e.g. ('week1', 'day1', 1)
                    weekClass = collection.find_one({'user_tel': user_tel, 'week': time[0]})
                    if not weekClass:
                        # 该周信息尚未登记
                        new_weekClass = {
                            'user_tel': user_tel,
                            'week': time[0],
                            'day1': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            'day2': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            'day3': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            'day4': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            'day5': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            'day6': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            'day7': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        }
                        new_weekClass[time[1]][time[2] - 1] = name
                        try:
                            collection.insert_one(new_weekClass).inserted_id
                        except:
                            print('save fail when {}, with the document does not exist before'.format(str(time)))
                            return False
                    else:
                        day = weekClass[time[1]]
                        day[time[2] - 1] = name
                        try:
                            collection.update_one({
                                'user_tel': user_tel,
                                'week': time[0],
                            },
                                {'$set': {time[1]: day}}
                            )
                        except:
                            print('save fail when {}, with the document exist before'.format(str(time)))
                            return False

                return True

            # 存放课表信息
            index = 0
            while index < len(tds):
                singleLesson = Lesson(name=tds[index], type=tds[index + 1], time=tds[index + 2], teacher=tds[index + 3], address=tds[index + 4])
                # print(singleLesson)
                if saveLessons(singleLesson.getTime(), singleLesson.getName() + '@' + singleLesson.getAddress()):
                    index += 5
                else:
                    print('save fail in loop')
                    return restful.server_error(message='存入数据库时发生错误')

            def saveWeekCalibration():
                # 存放开学第一周是本年度第几周
                firstWeek = collection.find_one({
                    'user_tel': user_tel,
                    'type': 'weekCalibration'
                })
                if not firstWeek:
                    # 尚未记录
                    new_firstWeek = {
                        'user_tel': user_tel,
                        'type': 'weekCalibration',
                        'firstWeek': startDate
                    }
                    try:
                        collection.insert_one(new_firstWeek).inserted_id
                    except:
                        print('save fail with firstweek, with the document does not exist before')
                        return False
                else:
                    try:
                        a = collection.update_one({
                            'user_tel': user_tel,
                            'type': 'weekCalibration',
                        },
                            {'$set': {'firstWeek': startDate}}
                        )
                    except:
                        print('save fail with firstweek, with the document exist before')
                        return False

                return True

            # 标定第一周
            if not saveWeekCalibration():
                return restful.server_error(message='第一周标定失败')

            return restful.success()
        else:
            return restful.params_error(message=form.get_error())

'''
邮箱设置接口
'''
@bp.route('/emailSetting/', methods=['POST'])
def emailSetting():
    email = request.form.get('email')
    if email:
        print('email: ', email)
        user = g.front_user
        user.email = email
        db.session.commit()
        return restful.success()
    else:
        return restful.params_error(message='邮箱格式错误')

'''
课表获取接口
'''
@bp.route('/lessons/', methods=['POST'])
def lessons():
    startdate = request.form.get('start')
    enddate = request.form.get('end')
    print('start: ', startdate)
    print('end: ', enddate)

    return restful.success()




bp.add_url_rule('/signup/', view_func=SignupView.as_view('signup'))
bp.add_url_rule('/signin/', view_func=SigninView.as_view('signin'))
bp.add_url_rule('/classSchedule/', view_func=ClassSchedule.as_view('classSchedule'))
