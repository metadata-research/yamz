# from app import data
from app import db
from app.io import io_blueprint as io
from app.io.data import (
    export_term_dict,
    import_term_dict,
    process_csv_upload,
)
from app.io.forms import DataFileUploadForm, EmptyForm
from app.term.models import TermSet
from flask import render_template, request, send_file, current_app
from flask_login import current_user, login_required
from app.term.helpers import get_ark_id


@login_required
@io.route("/upload", methods=["GET", "POST"])
def import_document():
    form = DataFileUploadForm()
    if form.validate_on_submit():
        uploaded_file = form.data_file.data
        set_name = form.name.data
        set_description = form.description.data
        owner_id = current_user.id
        new_set = TermSet(
            user_id=owner_id,
            source="upload",
            name=set_name,
            description=set_description,
        )
        new_set.save()
        db.session.refresh(new_set)
        term_dict = process_csv_upload(uploaded_file)
        term_set = import_term_dict(term_dict, new_set)
        term_list = term_set.terms
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
