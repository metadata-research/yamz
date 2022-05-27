from flask import render_template
from flask_login import current_user, login_required
from app.term.models import Term

from app.admin import admin_blueprint as admin


@admin.route("/console")
def index():
    return render_template("admin/index.jinja")
