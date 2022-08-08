from app import data
from app.io import io_blueprint as io
from app.io.forms import DataFileUploadForm
from flask import render_template, request


@io.route("/upload", methods=["GET", "POST"])
def import_document():
    form = DataFileUploadForm()
    if form.validate_on_submit():
        upload_document = form.data_file.data
        file_name = data.save(form.data_file.data)
        return file_name
    return render_template("io/import_document.jinja", form=form)


# return render_template("io/import_document.jinja", form=FileUploadForm())
