import io

from flask import render_template


from app.io import io_blueprint as io
from flask import render_template


@io.route("/import")
def import_document():
    return render_template("io/import_document.jinja")
