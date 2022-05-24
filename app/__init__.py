import logging
import os
from logging.handlers import RotatingFileHandler, SMTPHandler

from config import Config
from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_pagedown import PageDown

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
pagedown = PageDown()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."


def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    pagedown.init_app(app)

    from app.auth.models import AdminModelView, AppAdminIndexView

    admin = Admin(app, index_view=AppAdminIndexView(name="YAMZ Status"))

    from app.notify.signal_handlers import connect_handlers

    connect_handlers()

    from app.auth import auth_blueprint as auth_bp
    from app.error import error_blueprint as error_bp
    from app.main import main_blueprint as main_bp
    from app.notify import notify_blueprint as notify_bp
    from app.term import term_blueprint as term_bp
    from app.user import user_blueprint as user_bp

    app.register_blueprint(auth_bp, url_prefix="/")
    app.register_blueprint(error_bp, url_prefix="/error")
    app.register_blueprint(main_bp, url_prefix="/")
    app.register_blueprint(notify_bp, url_prefix="/notify")
    app.register_blueprint(term_bp, url_prefix="/term")
    app.register_blueprint(user_bp, url_prefix="/user")

    from app.term.models import Tag, Term
    from app.user.models import User

    admin.add_view(AdminModelView(User, db.session, endpoint="users"))
    admin.add_view(AdminModelView(Term, db.session, endpoint="terms"))
    admin.add_view(AdminModelView(Tag, db.session, endpoint="tags"))
    admin.add_link(MenuLink(name="Logout", category="", url="/logout?next=/admin"))

    if not app.debug and not app.testing:
        if app.config["MAIL_SERVER"]:
            auth = None
            if app.config["MAIL_USERNAME"] or app.config["MAIL_PASSWORD"]:
                auth = (app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
            secure = None
            if app.config["MAIL_USE_TLS"]:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
                fromaddr=app.config["MAIL_USERNAME"],
                toaddrs=app.config["ADMINS"],
                subject="YAMZ Error",
                credentials=auth,
                secure=secure,
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if app.config["LOG_TO_STDOUT"]:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists("logs"):
                os.mkdir("logs")
            file_handler = RotatingFileHandler(
                "logs/yamz.log", maxBytes=10240, backupCount=10
            )
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s %(levelname)s: %(message)s "
                    "[in %(pathname)s:%(lineno)d]"
                )
            )
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info("YAMZ startup")

    return app
