# from app import data
from app.io import io_blueprint as io
from app.io.forms import DataFileUploadForm
from flask import render_template

from app.io.data import process_csv_upload


@io.route("/upload", methods=["GET", "POST"])
def import_document():
    form = DataFileUploadForm()
    if form.validate_on_submit():
        uploaded_file = form.data_file.data
        term_list = process_csv_upload(uploaded_file)
        return render_template("io/import_results.jinja", term_list=term_list)

    return render_template("io/import_document.jinja", form=form)
