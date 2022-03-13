from flask import Blueprint

error_blueprint = Blueprint("error", __name__, template_folder="templates")

from app.error import handlers
