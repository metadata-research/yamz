from config import Config, TestConfig
from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."

# admin = Admin()


def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(config_class)

    from app.auth.models import AdminModelView, AppAdminIndexView

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    admin = Admin(app, index_view=AppAdminIndexView(name="YAMZ Status"))

    from app.auth import auth_blueprint as auth_bp
    from app.error import error_blueprint as error_bp
    from app.main import main_blueprint as main_bp
    from app.term import term_blueprint as term_bp
    from app.term.models import Tag, Term
    from app.user import user_blueprint as user_bp

    # from app.admin import admin_blueprint as admin_bp
    from app.user.models import User

    app.register_blueprint(main_bp, url_prefix="/")
    app.register_blueprint(auth_bp, url_prefix="/")
    app.register_blueprint(term_bp, url_prefix="/term")
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(error_bp, url_prefix="/error")
    # app.register_blueprint(admin_bp, url_prefix="/admin")

    admin.add_view(AdminModelView(User, db.session, endpoint="users"))
    admin.add_view(AdminModelView(Term, db.session, endpoint="terms"))
    admin.add_view(AdminModelView(Tag, db.session, endpoint="tags"))
    admin.add_link(MenuLink(name="Logout", category="", url="/logout?next=/admin"))

    return app
