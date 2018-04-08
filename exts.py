#encoding: utf-8

from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from utils.yunpian import YunpianAPI

db = SQLAlchemy()
mail = Mail()
yunpian = YunpianAPI()