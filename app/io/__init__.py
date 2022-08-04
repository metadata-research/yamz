from flask import Blueprint

io_blueprint = Blueprint("export", __name__, template_folder="templates")

from app.io import views
