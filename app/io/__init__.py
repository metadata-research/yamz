from flask import Blueprint

io_blueprint = Blueprint("io", __name__, template_folder="templates")

from app.io import views
