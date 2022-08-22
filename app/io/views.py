# from app import data
from app.io import io_blueprint as io
from app.io.forms import DataFileUploadForm, EmptyForm
from flask import render_template, request, send_file
from flask_login import login_required

from app.io.data import (
    import_term_dict,
    process_csv_upload,
    export_term_dict,
)


@login_required
@io.route("/upload", methods=["GET", "POST"])
def import_document():

    form = DataFileUploadForm()
    if form.validate_on_submit():
        uploaded_file = form.data_file.data
        term_dict = process_csv_upload(uploaded_file)
        term_list = import_term_dict(term_dict)
        return render_template(
            "io/import_results.jinja", selected_terms=term_list, form=EmptyForm()
        )

    return render_template("io/import_document.jinja", form=form)


@io.route("/export", methods=["GET", "POST"])
def export_page():
    return render_template("io/export.jinja")


@io.route("/export/terms", methods=["GET", "POST"])
def export_term_results():
    search_terms = request.args.get("search_terms")
    response = export_term_dict(search_terms)
    return response
    #
    # return render_template("io/export_terms.jinja", terms=term_list)
