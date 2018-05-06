#encoding: utf-8
from flask import Flask
from apps.cms import bp as cms_bp
from apps.common import bp as common_bp
from apps.front import bp as front_bp
import config
from exts import db, mail, yunpian
from flask_wtf import CSRFProtect

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    yunpian.init_app(app)
    CSRFProtect(app)

    app.register_blueprint(cms_bp)
    app.register_blueprint(common_bp)
    app.register_blueprint(front_bp)

    return app


if __name__ == '__main__':
    app = create_app()
    # app.run(host='0.0.0.0')
    app.run()

