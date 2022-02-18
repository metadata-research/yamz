from flask import Flask
from config import Config, TestConfig
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(TestConfig)

db = SQLAlchemy(app)

from app.user.models import User, AnonymousUser

login_manager = LoginManager(app)
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."
login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


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
