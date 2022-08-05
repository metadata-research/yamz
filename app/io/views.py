from flask import render_template


from app.io import io_blueprint as io
from flask import render_template
from app.io.forms import FileUploadForm
from app import documents


@io.route("/import")
def import_document():
    form = FileUploadForm()
    if form.validate_on_submit():
        document_filename = documents.save(form.document_file.data)
        document_url = documents.url(document_filename)
        return "<a href='{}'>{}</a>".format(document_url, document_filename)

    return render_template("io/import_document.jinja", form=form)
