from flask import Flask
from config import Config, TestConfig
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_admin import Admin

from flask_admin.contrib.sqla import ModelView

db = SQLAlchemy()
migrate = Migrate()

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."

admin = Admin()


def create_app(config_class=TestConfig):

    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    admin.init_app(app)

    from app.main import main_blueprint as main_bp
    from app.auth import auth_blueprint as auth_bp
    from app.term import term_blueprint as term_bp
    from app.user import user_blueprint as user_bp

    # from app.admin import admin_blueprint as admin_bp

    from app.user.models import User
    from app.term.models import Term, Tag

    app.register_blueprint(main_bp, url_prefix="/")
    app.register_blueprint(auth_bp, url_prefix="/")
    app.register_blueprint(term_bp, url_prefix="/term")
    app.register_blueprint(user_bp, url_prefix="/user")
    # app.register_blueprint(admin_bp, url_prefix="/admin")

    admin.add_view(ModelView(User, db.session, endpoint="users"))
    admin.add_view(ModelView(Term, db.session, endpoint="terms"))
    admin.add_view(ModelView(Tag, db.session, endpoint="tags"))
    return app
