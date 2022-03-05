from flask import Blueprint

admin_blueprint = Blueprint("admin", __name__, template_folder="templates")

from app.admin import views
