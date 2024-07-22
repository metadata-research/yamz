from flask import (render_template, g)
from flask_login import current_user

from app.main import main_blueprint as main
from app.term.forms import SearchForm
from app.term.models import Term, Tag
from markupsafe import escape
from werkzeug.exceptions import abort

@main.route("/p/<portal_tag>")
def portal_index(portal_tag):
    portal_tag = escape(portal_tag)
    tag = Tag.query.filter_by(value=portal_tag).first()
    if not tag:
        abort(404)
    g.search_form = SearchForm()
    page = 1
    per_page = 10
    term_list = Term.query.filter(Term.tags.any(value=portal_tag)).order_by(Term.term_string)

    return render_template(
        "main/portal.jinja",
        my_terms=term_list,
        tracked_terms=[],
        search_form=g.search_form,
        portal_tag=portal_tag,
    )


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
