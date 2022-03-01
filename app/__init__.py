from flask import Flask
from config import Config, TestConfig
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."


def create_app(config_class=TestConfig):

    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.auth import views
    from app.main import views
    from app.term import views
    from app.user import views

    from app.main import main_blueprint as main_bp
    from app.auth import auth_blueprint as auth_bp
    from app.term import term_blueprint as term_bp
    from app.user import user_blueprint as user_bp

    app.register_blueprint(main_bp, url_prefix="/")
    app.register_blueprint(auth_bp, url_prefix="/")
    app.register_blueprint(term_bp, url_prefix="/term")
    app.register_blueprint(user_bp, url_prefix="/user")

    @app.template_filter("format_date")
    def format_date(date):
        return date.strftime("%Y.%m.%d")

    return app
