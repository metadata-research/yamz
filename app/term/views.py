from flask import render_template
from app.term import term_blueprint as term


@term.route("/")
def index():
    return "Hello, world!"


@term.route("/list")
def list():
    return render_template("term/list.html")


@term.route("/<term>")
def term_page(term):
    return render_template("term/index.jinja", term=term)
