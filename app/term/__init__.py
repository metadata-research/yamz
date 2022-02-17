from flask import Blueprint

term_blueprint = Blueprint("term", __name__, template_folder="templates")

from app.term import views
