from flask import render_template, request
from app import db
from app.error import error_blueprint as error


@error.app_errorhandler(404)
def not_found_error(error):
    return render_template("error/404.jinja"), 404


@error.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template("error/500.jinja"), 500
