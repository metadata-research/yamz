from flask import render_template
from flask_login import current_user, login_required
from app.term.models import Term

from app.admin import admin_blueprint as admin


@admin.route("/console")
def index():
    return render_template("admin/index.jinja")


@admin.route("/split")
def split():
    terms = Term.query.filter(Term.definition.contains("#{g: xqGCW | h1619}"))
    return render_template("admin/split_terms.jinja", terms=terms)
