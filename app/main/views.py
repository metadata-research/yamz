from flask import (render_template, g)
from flask_login import current_user

from app.main import main_blueprint as main
from app.term.forms import SearchForm

@main.route("/")
def index():
    g.search_form = SearchForm()
    if current_user.is_authenticated:
        my_terms = current_user.terms
        tracked_terms = current_user.tracking
    else:
        my_terms = []
        tracked_terms = []
    return render_template(
        "main/index.jinja",
        my_terms=my_terms,
        tracked_terms=tracked_terms,
        search_form=g.search_form,
    )


@main.route("/about")
def about():
    return render_template("main/about.jinja")


@main.route("/contact")
def contact():
    return render_template("main/contact.jinja")


@main.route("/guidelines")
def guidelines():
    return render_template("main/guidelines.jinja")
