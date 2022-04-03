from flask import Blueprint

notify_blueprint = Blueprint("notify", __name__, template_folder="templates")

from app.notify import views
