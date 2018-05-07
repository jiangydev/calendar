# mencoding: utf-8

import re
import requests
import time
from lxml import etree
from PIL import Image
from io import BytesIO
from urllib import parse

class ZhengfangSpider:
    '''
    ZhengfangSpider，用于NJIT正方教务系统学生课表爬取

    :: __init__(self, studentNum, password, baseUrl='http://jwjx.njit.edu.cn/default2.aspx')
    用于初始化目标学生对象信息
    接收：
        - studentNum: [str] 学生学号
        - password: [str] 正方系统密码
        - baseUrl: [str] (optional) 网址域名, default:'http://jwjx.njit.edu.cn'

    :: login(self)
    登录教务系统，取得cookie(必须)
    返回：
        - loginResult [boolean]
            True表示登录成功，False表示登录失败

    :: identifyCaptcha(self, captchaResp):
    识别验证码图片，根据识别方式不同，可以重写此方法
    :param captchaResp: [requests.models.Response] 请求验证码接口后的返回信息,其内容为可以解析成gif格式的图pain
    :return: [str] 识别的验证码字符串
    '''


    def __init__(self, studentNum='123456789', password='123456789', baseUrl='http://jwjx.njit.edu.cn'):
        self.studentNum = studentNum
        self.password = password
        self.baseUrl = baseUrl
        self.session = requests.Session()
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'
        # self.session.headers['Connection'] = 'close'

    def parseVIEWSTATE(self, response):
        parser = etree.HTMLParser(encoding='utf-8')
        html = etree.HTML(response.text, parser=parser)
        VIEWSTATE = html.xpath("//input[@name='__VIEWSTATE']//@value")[0]
        return VIEWSTATE

    def identifyCaptcha(self, captchaBin):
        '''
        identifyCaptcha(self, captchaResp):
        识别验证码图片，根据识别方式不同，可以重写此方法
        :param captchaResp: [requests.models.Response] 请求验证码接口后的返回信息,其内容为可以解析成gif格式的图pain
        :return: [str] 识别的验证码字符串
        '''
        img = Image.open(BytesIO(captchaBin))
        img.save('001.gif')
        # 手动输入验证码
        captcha = input("input the captcha here: ")
        return captcha

    def prelogin(self):
        ''' 获取登录界面信息，验证码'''
        # 取得登录界面
        self.loginUrl = self.baseUrl + '/Default2.aspx'
        response = self.session.get(self.loginUrl)
        time.sleep(0.1)  # suspend 0.1 second from requests crash
        self.__VIEWSTATE = self.parseVIEWSTATE(response)
        # 获取验证码信息
        imgUrl = self.baseUrl + '/CheckCode.aspx?'
        imgResponse = self.session.get(imgUrl)
        time.sleep(0.1)
        if imgResponse.status_code == requests.codes.ok:
            self.captchaBin = imgResponse.content
        else:
            print('request captcha fail')
            return False

    def login(self, captcha=''):
        self.loginUrl = self.baseUrl + '/Default2.aspx'
        if captcha == '':
            captcha = self.identifyCaptcha(self.captchaBin)
        else:
            captcha = captcha

        # 构造登录Post请求数据
        RadioButtonList1 = u"学生".encode('gb2312', 'replace')
        data = {
            "RadioButtonList1": RadioButtonList1,
            "__VIEWSTATE": self.__VIEWSTATE,
            "txtUserName": self.studentNum,
            "Textbox1": "",
            "TextBox2": self.password,
            "txtSecretCode": captcha,
            "Button1": "",
            "lbLanguage": "",
            "hidPdrs": "",
            "hidsc": ""
        }

        # 请求登录
        loginResponse = self.session.post(self.loginUrl, data=data)
        time.sleep(0.1)
        if loginResponse.status_code == requests.codes.ok:
            print('login ZhengFang successfully')
            self.studentName = self.getStudentName(loginResponse)
            return True
        else:
            print('login ZhengFang fail')
            return False

    def getStudentName(self, response):
        '''
        getStudentName
        解析登录后主页，获取学生姓名
        :param response: [requests.models.Response] 登录主页成功的response
        :return: [str] 学生姓名
        '''
        html = etree.HTML(response.text)
        # 结尾带“同学”的姓名, e.g. '骚杰同学'
        nameTX = html.xpath("//span[@id='xhxm']/text()")[0]
        return nameTX[:-2]

    def getClassSchedule(self):
        self.session.headers['Refer'] = self.baseUrl + "/xs_main.aspx?xh=" + self.studentNum
        qsdata = {
            'xh': self.studentNum,
            'xm': self.studentName,
            'gnmkdm': 'N121603'
        }
        qs = parse.urlencode(qsdata, encoding='gb2312')
        classUrl = self.baseUrl + '/xskbcx.aspx?' + qs
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
        (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36',
            'Referer': 'http://jwjx.njit.edu.cn/xs_main.aspx?xh=' + self.studentNum,
            'Host': 'jwjx.njit.edu.cn',
            'Cache-Control': 'no-cache'
        }
        print(classUrl)
        classResponse = self.session.get(classUrl, headers=headers)
        time.sleep(0.1)
        return classResponse.text

    def getCaptchaBin(self):
        return self.captchaBin

    def setId(self, id):
        self.studentNum = id

    def setPwd(self, pwd):
        self.password = pwd

    def getviewstate(self):
        return self.__VIEWSTATE

    def setViewstate(self, raw):
        self.__VIEWSTATE = raw

class Lesson():
    '''Lesson
    接收课程信息，并对形式做以定转换
    '''

    def __init__(self, name, time, address, teacher, type):
        '''
        :param name: [str] e.g.: 工业机器人控制技术
        :param time: [str] e.g.: 周二第1,2节{第11-11周|单周}
        :param address: [str] e.g.: 南A302
        :param teacher: [str] e.g.: 刘娣
        :param type: [str] e.g.: 必修
        '''
        self.name = name
        self.time = time
        self.address = address
        self.teacher = teacher
        self.type = type

    def __str__(self):
        return '-'.join([self.name, self.time, self.address, self.teacher, self.type])

    def getName(self):
        ''':return the name of the lesson'''
        return self.name

    def getAddress(self):
        ''':return return the classroom of lesson'''
        return self.address

    def getTime(self):
        '''Lesson::getTime
        format time information("周一第7,8节{第1-6周}") into [('week1', 'day1', 1), ('week2', 'day2', 2), ...],
        for example, [('week1', 'day1', 1)] means the class appears at the first lesson on Monday in the first week
        return:
            list for the classtime in the form of [(week, day, lesson)]
        '''

        # group: 1-day, 2-lesson_start, 3-lesson_end, 4-week_start, 5-week-end
        m = re.match(r'^周(\w)第(\d{1,2}),(\d{1,2})节{第(\d{1,2})-(\d{1,2})周*', self.time)
        chars = ['一', '二', '三', '四', '五', '六', '日']

        try:
            # 注意：group(0)是匹配的字符串自身
            day = chars.index(m.group(1))+1     # Monday
            weeks = list(range(int(m.group(4)), int(m.group(5))+1)) # week 1->10
            lessons = list(range(int(m.group(2)), int(m.group(3))+1)) # lesson 5->8
        except AttributeError:
            print("regular expression gets nothing")
            raise AttributeError
        except ValueError:
            print("regular expression gets someting wrong")
            raise ValueError

        def even_or_odd(numType, nums):
            '''
            even_or_odd(numType, nums)
            check a list of ints and delete odd or even numbers
            :param numType: str, 'even' means needs even numbers, 'odd' means needs odd numbers
            :param nums: list, ints to be handled
            :return: list after handling
            '''
            if numType == 'even':
                for num in nums:
                    if num % 2 != 0:
                        nums.remove(num)
            elif numType == 'odd':
                for num in nums:
                    if num % 2 == 0:
                        nums.remove(num)
            else:
                raise ValueError("except 'odd' or 'even', but got none of them")
            return nums


        if '单' in set(self.time):
            weeks = even_or_odd('odd', weeks)
        elif '双' in set(self.time):
            weeks = even_or_odd('even', weeks)

        times = []
        for week in weeks:
            for lesson in lessons:
                times.append(('week'+str(week), 'day'+str(day), lesson))

        return times