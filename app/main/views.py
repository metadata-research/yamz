from flask import render_template
from flask_login import current_user, login_required

from app.main import main_blueprint as main
from app.term.models import Term, Track
from app.term.forms import SearchForm


@main.route("/")
def index():
    search_form = SearchForm()
    my_terms = current_user.terms.all()
    tracked_terms = Track.query.filter_by(user_id=current_user.id).all()
    return render_template(
        "main/index.jinja",
        my_terms=my_terms,
        tracked_terms=tracked_terms,
        search_form=search_form,
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
