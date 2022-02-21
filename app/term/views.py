from flask import render_template
from app.term import term_blueprint as term


@term.route("/")
def index():
    return "Hello, world!"
