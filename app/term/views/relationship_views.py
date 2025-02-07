"""
This module handles the views for managing relationships between terms.
A relationship consists of two terms (parent and child) joined by a predicate where one term is the subject and the
other the object.
Relationships are attached to termsets and not to the terms themselves for now.
"""

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from typing import List, Optional, Any

from app.term import term_blueprint as term
from app.term.forms import AddRelationshipForm, EditRelationshipForm
from app.term.models import Ark, Relationship, Tag, Term


@term.route("/relationship", methods=["GET", "POST"])
def display_relation(output: Any) -> Any:
    return output


def get_terms_with_predicate_tag() -> List[Term]:
    """Retrieve terms with the `rdfs:predicate` tag."""
    return Term.query.filter(Term.tags.any(Tag.value == "rdfs:predicate")).all()


@term.route("/relationship/add/", methods=["GET", "POST"])
@login_required
def add_relationship():
    term_list = get_terms_with_predicate_tag()
    choices = [("", "Select a relationship")] + [
        (term.concept_id, term.term_string) for term in term_list
    ]

    relationship_form = AddRelationshipForm()
    relationship_form.predicate_id.choices = choices

    if relationship_form.validate_on_submit():
        subject = Term.query.filter_by(
            concept_id=relationship_form.subject_id.data
        ).first()
        predicate = Term.query.filter_by(
            concept_id=relationship_form.predicate_id.data
        ).first()
        obj = Term.query.filter_by(concept_id=relationship_form.object_id.data).first()

        if not subject or not predicate or not obj:
            flash("Error: One or more terms could not be found.", "danger")
            return redirect(url_for("term.add_relationship"))

        ark = Ark().create_ark(shoulder="g1", naan="13183")
        new_relationship = Relationship(
            parent_id=subject.id,
            predicate_id=predicate.id,
            child_id=obj.id,
            ark_id=ark.id,
            owner_id=current_user.id,
        )
        new_relationship.save()

        return subject.term_string + predicate.term_string + obj.term_string

    return render_template(
        "relationship/add_relationship.jinja", form=relationship_form
    )


@term.route("/relationship/edit/<int:relationship_id>", methods=["GET", "POST"])
@login_required
def edit_relationship(relationship_id: int):
    relationship = Relationship.query.get_or_404(relationship_id)
    term_list = get_terms_with_predicate_tag()
    choices = [("", "Select a relationship")] + [
        (term.concept_id, term.term_string) for term in term_list
    ]

    relationship_form = EditRelationshipForm()
    relationship_form.predicate_id.choices = choices

    if request.method == "GET":
        subject_term = Term.query.get(relationship.child_id)
        predicate_term = Term.query.get(relationship.predicate_id)
        object_term = Term.query.get(relationship.parent_id)

        relationship_form.subject_term_string.data = (
            subject_term.term_string if subject_term else ""
        )
        relationship_form.predicate_id.data = relationship.predicate_id
        relationship_form.object_term_string.data = (
            object_term.term_string if object_term else ""
        )

    if relationship_form.validate_on_submit():
        subject = Term.query.filter_by(
            concept_id=relationship_form.subject_id.data
        ).first()
        predicate = Term.query.filter_by(
            concept_id=relationship_form.predicate_id.data
        ).first()
        obj = Term.query.filter_by(concept_id=relationship_form.object_id.data).first()

        if not subject or not predicate or not obj:
            flash("Error: One or more terms could not be found.", "danger")
            return redirect(
                url_for("term.edit_relationship", relationship_id=relationship_id)
            )

        relationship.child_id = subject.id
        relationship.predicate_id = predicate.id
        relationship.parent_id = obj.id
        relationship.save()

        return redirect(
            url_for("term.display_relationship", relationship_id=relationship_id)
        )

    return render_template(
        "relationship/edit_relationship.jinja",
        form=relationship_form,
        relationship=relationship,
    )


@term.route("/relationship/display/<int:relationship_id>")
def display_relationship(relationship_id: int):
    relationship = Relationship.query.get_or_404(relationship_id)
    return render_template(
        "relationship/display_relationship.jinja", relationship=relationship
    )


@term.route("/relationship/delete/<int:relationship_id>", methods=["POST"])
@login_required
def delete_relationship(relationship_id: int):
    relationship = Relationship.query.get_or_404(relationship_id)
    term_set_id = request.args.get("term_set_id")
    relationship.delete()
    flash("Relationship deleted.")
    return redirect(
        url_for("term.display_termset", term_set_id=term_set_id, tab="relationships")
    )


@term.route("/relationship/list/")
def list_properties():
    relationships = Relationship.query.all()
    return render_template(
        "relationship/list_properties.jinja", relationships=relationships
    )
