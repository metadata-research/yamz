from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

from app.user.models import User

from app.main import views
from app.term import views
from app.user import views

from app.main import main_blueprint as main_bp
from app.term import term_blueprint as term_bp
from app.user import user_blueprint as user_bp

app.register_blueprint(main_bp, url_prefix="/")
app.register_blueprint(term_bp, url_prefix="/term")
app.register_blueprint(user_bp, url_prefix="/user")
