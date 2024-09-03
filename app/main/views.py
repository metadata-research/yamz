from flask import (render_template, g)
from flask_login import current_user

from app.main import main_blueprint as main
from app.term.forms import SearchForm
from app.term.models import Term, Tag
from markupsafe import escape
from werkzeug.exceptions import abort
from flask import redirect, url_for, session

def check_tag(portal_tag):
    tag = Tag.query.filter_by(value=portal_tag).first()
    if not tag:
        abort(404)

@main.route("/leave_portal")
def leave_portal():
    session["old_portal_tag"] = session.pop("portal_tag", None)
    return redirect(url_for("main.index"))

@main.route("/p/<portal_tag>")
def portal_index(portal_tag):
    session.pop("old_portal_tag", None)
    portal_tag = escape(portal_tag)
    tag = Tag.query.filter_by(value=portal_tag).first()
    if not tag:
        abort(404)
    session["portal_tag"] = portal_tag
    g.search_form = SearchForm(portal_tag=portal_tag)
    page = 1
    per_page = 10
    term_list = Term.query.filter(Term.tags.any(value=portal_tag)).order_by(Term.term_string)

    if current_user.is_authenticated:
        my_terms = current_user.terms
        tracked_terms = current_user.tracking
    else:
        my_terms = []
        tracked_terms = []

    return render_template(
        "main/portal.jinja",
        my_terms=my_terms,
        tracked_terms=tracked_terms,
        search_form=g.search_form,
        #portal_tag=session.get("portal_tag"),
    )


@main.route("/")
def index():
    if session.get("portal_tag"):
        return redirect(url_for("main.portal_index", portal_tag=session.get("portal_tag")))
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


@main.route("/about/<portal_tag>")
@main.route("/about")
def about(portal_tag=''):
    return render_template("main/about.jinja", portal_tag=portal_tag)


@main.route("/contact")
def contact():
    return render_template("main/contact.jinja")


@main.route("/guidelines/<portal_tag>")
@main.route("/guidelines")
def guidelines(portal_tag=''):
    return render_template("main/guidelines.jinja", portal_tag=portal_tag)
