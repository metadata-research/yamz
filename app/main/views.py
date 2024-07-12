from flask import (render_template, g)
from flask_login import current_user

from app.main import main_blueprint as main
from app.term.forms import SearchForm
from app.term.models import Term, Tag
from markupsafe import escape

@main.route("/portal/<portal_type>")
def portal(portal_type):
    g.search_form = SearchForm()
    portal_type = escape(portal_type)
    # get terms with Tags that have the value "portal" and the name of the portal type
    page = 1
    per_page = 10
    tag = Tag.query.get_or_404(144)
    term_list = Term.query.filter(Term.tags.any(id=144)).order_by(Term.term_string)
    
    return render_template(
        "main/index.jinja",
        my_terms=term_list,
        tracked_terms=[],
        search_form=g.search_form,
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
