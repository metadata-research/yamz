from flask import render_template
from flask_login import current_user, login_required
from app.term.models import Term

from app.admin import admin_blueprint as admin
from app.admin.term import *


@admin.route("/console")
def index():
    return render_template("admin/index.jinja")


@admin.route("/split")
def split():
    terms = findGCW()  # find all terms with the tag #{g: xqGCW | h1619}
    return render_template("admin/split_terms.jinja", terms=terms)
