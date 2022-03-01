from flask import Blueprint

error_blueprint = Blueprint("error", __name__)

from app.error import handlers
