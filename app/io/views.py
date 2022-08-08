# from app import data
from app.io import io_blueprint as io
from app.io.forms import DataFileUploadForm
from flask import render_template

from app.io.data import import_term_dict, process_csv_upload


@io.route("/upload", methods=["GET", "POST"])
def import_document():
    form = DataFileUploadForm()
    if form.validate_on_submit():
        uploaded_file = form.data_file.data
        term_dict = process_csv_upload(uploaded_file)
        import_success = import_term_dict(term_dict)
        return render_template("io/import_results.jinja", term_list=term_dict)

    return render_template("io/import_document.jinja", form=form)
