from flask import Blueprint

export_blueprint = Blueprint("export", __name__, template_folder="templates")

from app.term import views
