import os
from flask import (
    flash,
    redirect,
    render_template,
    send_file,
    url_for,
    request,
    current_app,
)
from flask_login import current_user, login_required

# Import Blueprints, Forms, Models, and Utilities
from app.term import term_blueprint as term
from app.term.forms import EmptyForm, AddTagForm, EditTermSetForm, AddSubClassForm
from app.term.models import TermSet, Tag, Term, Ark, Relationship
from app.term.models.association_tables import termset_relationships
from app.term.views.list_views import *

from app.user.models import User
from typing import Dict, Any, List, Union
from flask import Response


# Route Handlers
@term.route("/set/list")
def list_termsets():
    term_sets = TermSet.query.order_by(TermSet.name)
    return render_template("termset/list_termsets.jinja", term_sets=term_sets)


@term.route("/set/display/<int:term_set_id>")
def display_termset(term_set_id: int):
    term_set = TermSet.query.get_or_404(term_set_id)
    tag_form = AddTagForm()
    add_subclass_form = AddSubClassForm()
    tag_form.tag_list.choices = [
        (tag.id, tag.value) for tag in Tag.query.order_by(Tag.value).all()
    ]

    return render_template(
        "termset/display_termset.jinja",
        term_set=term_set,
        form=EmptyForm(),
        tag_form=tag_form,
        subclass_form=add_subclass_form,
    )


@term.route("/set/add_subclass/<int:term_set_id>", methods=["POST"])
@login_required
def add_subclass(term_set_id: int) -> Response:
    term_set = TermSet.query.get_or_404(term_set_id)
    form = AddSubClassForm()

    rdfs_subclass = Term.query.filter_by(term_string="rdfs:subClassOf").first()
    child_term = Term.query.filter_by(concept_id=form.child_id.data).first()

    if not child_term:
        flash("Error: Child term not found.")
        return redirect(
            url_for("term.display_termset", term_set_id=term_set_id, tab="classes")
        )

    if form.validate_on_submit():
        relationship = Relationship(
            parent_id=form.parent_term_id.data,
            predicate_id=rdfs_subclass.id,
            child_id=child_term.id,
            owner_id=current_user.id,
            ark_id=Ark().create_ark(shoulder="g1", naan="13183").id,
            created=db.func.now(),
            modified=db.func.now(),
        )

        subclass_tag = Tag.query.filter_by(value="subclass_added").first()
        if subclass_tag:
            relationship.tags.append(subclass_tag)

        db.session.add(relationship)
        term_set.relationships.append(relationship)

        if child_term not in term_set.terms:
            term_set.terms.append(child_term)




@term.route("/set/delete/<int:term_set_id>", methods=["POST"])
@login_required
def delete_term_set(term_set_id: int) -> Response:
    term_set = TermSet.query.get_or_404(term_set_id)
    if term_set.user_id == current_user.id or current_user.is_administrator:
        db.session.delete(term_set)
        db.session.commit()
        flash("Term set deleted.")
    else:
        flash("You are not authorized to delete this term set.")
    return redirect(url_for("term.list_termsets"))


@term.route("/set/add_tag/<int:term_set_id>", methods=["POST"])
@login_required
def add_tag_to_term_set(term_set_id: int) -> Response:
    term_set = TermSet.query.get_or_404(term_set_id)
    tag_form = AddTagForm()
    tag_form.tag_list.choices = [
        (tag.id, tag.value) for tag in Tag.query.order_by(Tag.value).all()
    ]

    if tag_form.validate_on_submit():
        tag = Tag.query.get(tag_form.tag_list.data)
        if tag and tag not in term_set.tags:
            term_set.tags.append(tag)
            db.session.commit()
            flash("Tag added.")
        else:
            flash("Tag already exists in the term set.")
    else:
        flash("Error: Form validation failed.")

    return redirect(url_for("term.display_termset", term_set_id=term_set_id))


@term.route("/set/remove_tag/<int:term_set_id>/<int:tag_id>", methods=["POST"])
@login_required
def remove_tag_from_term_set(term_set_id: int, tag_id: int) -> Response:
    term_set = TermSet.query.get_or_404(term_set_id)
    tag = Tag.query.get_or_404(tag_id)

    if tag in term_set.tags:
        term_set.tags.remove(tag)
        db.session.commit()
        flash("Tag removed.")
    else:
        flash("Tag not found in term set.")

    return redirect(url_for("term.display_termset", term_set_id=term_set_id))


@term.route("/set/download_file/<filename>", methods=["GET"])
@login_required
def download_file(filename: str) -> Union[Response, str]:
    import_dir = os.path.join(current_app.root_path, "io", "import")
    file_path = os.path.join(import_dir, filename)

    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        flash("File not found.")
        return redirect(url_for("term.list_termsets"))




@term.route("/set/copy/<int:term_set_id>", methods=["POST"])
@login_required
def copy_termset(term_set_id: int) -> Response:
    original_term_set = TermSet.query.get_or_404(term_set_id)
    new_term_set = TermSet(
        name=f"Copy of {original_term_set.name}",
        description=original_term_set.description,
        source=original_term_set.source,
        user_id=current_user.id,
        created=db.func.now(),
        updated=db.func.now(),
    )
    db.session.add(new_term_set)

    new_term_set.tags.extend(original_term_set.tags)
    new_term_set.terms.extend(original_term_set.terms)

    db.session.commit()
    flash("Term set copied successfully.")
    return redirect(url_for("term.edit_termset", term_set_id=new_term_set.id))


@term.route("/set/simple/<int:term_set_id>")
def display_simple_termset(term_set_id: int):
    term_set = TermSet.query.get_or_404(term_set_id)
    return render_template("termset/display_simple_termset.jinja", term_set=term_set)
