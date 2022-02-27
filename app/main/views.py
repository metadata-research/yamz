from flask import render_template
from flask_login import current_user, login_required

from app.main import main_blueprint as main


@main.route("/")
def index():
    my_terms = current_user.terms.all()
    return render_template("main/index.jinja", my_terms=my_terms)


@main.route("/about")
def about():
    return render_template("main/about.jinja")


@main.route("/contact")
def contact():
    return render_template("main/contact.jinja")


@main.route("/guidelines")
def guidelines():
    return render_template("main/guidelines.jinja")
