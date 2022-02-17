from flask import render_template
from app.main import main_blueprint as main


@main.route("/")
def index():
    return render_template("main/index.jinja")


@main.route("/about")
def about():
    return render_template("main/about.jinja")


@main.route("/contact")
def contact():
    return render_template("main/contact.jinja")


@main.route("guidelines")
def guidelines():
    return render_template("main/guidelines.jinja")
