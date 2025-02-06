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

# Utility Functions
def get_hierarchy_data(term_set_id: int) -> Dict[str, Any]:
    """
    Builds a hierarchical structure for the given term set based on SubClass
    <Object(Child)> <Predicate:isSubClassOf> <Subject(Parent) using networkx.

    Args:
        term_set_id (int): The ID of the term set.

    Returns:
        dict: A nested dictionary representing the hierarchy.
    """
    term_set = TermSet.query.get_or_404(term_set_id)
    classifier = OntologyClassifier(term_set)
    hierarchy = classifier.build_hierarchy()

    root = [node for node, degree in hierarchy.in_degree() if degree == 0]
    if not root:
        flash("No root node found for the hierarchy.")
        return redirect(url_for("term.display_termset", term_set_id=term_set_id))

    def build_tree(node):
        children = list(hierarchy.successors(node))
        return {
            "name": node,
            "definition": hierarchy.nodes[node].get(
                "definition", "No definition available"
            ),
            "children": [build_tree(child) for child in children],
        }

    return build_tree(root[0])


def populate_relationships(relationships: List[Relationship], term_set: TermSet) -> List[Relationship]:
    """
    Populates the relationships with their associated terms, owners, and ARKs.

    Args:
        relationships (List[Relationship]): The list of relationships to populate.
        term_set (TermSet): The term set to which the relationships belong.

    Returns:
        List[Relationship]: The list or relationships that turns the id keys into their model representation.
    """
    for relationship in relationships:
        relationship.parent = Term.query.get(relationship.parent_id)
        relationship.predicate = Term.query.get(relationship.predicate_id)
        relationship.child = Term.query.get(relationship.child_id)
        relationship.owner = User.query.get(relationship.owner_id)
        relationship.ark = Ark.query.get(relationship.ark_id)

    return relationships


def log_form_errors(form: Any) -> None:
    for field, errors in form.errors.items():
        for error in errors:
            current_app.logger.error(f"Error in {field}: {error}")


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
    hierarchy_data = get_hierarchy_data(term_set_id)
    relationships = populate_relationships(term_set.relationships, term_set)

    return render_template(
        "termset/display_termset.jinja",
        term_set=term_set,
        form=EmptyForm(),
        tag_form=tag_form,
        subclass_form=add_subclass_form,
        relationships=relationships,
        hierarchy=hierarchy_data,
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

        db.session.commit()
        flash("Subclass added successfully.")
    else:
        log_form_errors(form)
        flash("Error: Form validation failed.")

    return redirect(
        url_for("term.display_termset", term_set_id=term_set_id, tab="classes")
    )


@term.route("/set/edit/<int:term_set_id>", methods=["GET", "POST"])
@login_required
def edit_termset(term_set_id: int) -> Union[str, Response]:
    term_set = TermSet.query.get_or_404(term_set_id)
    form = EditTermSetForm(obj=term_set)

    if form.validate_on_submit():
        form.populate_obj(term_set)
        db.session.commit()
        flash("Term set updated.")
        return redirect(url_for("term.display_termset", term_set_id=term_set_id))
    else:
        if request.method == "POST":
            flash("Error: Form validation failed.")
            log_form_errors(form)

    return render_template("termset/edit_termset.jinja", form=form, term_set=term_set)


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


@term.route("/set/classify_ontology/<int:term_set_id>")
@login_required
def classify_ontology(term_set_id: int):
    term_set = TermSet.query.get_or_404(term_set_id)
    classifier = OntologyClassifier(term_set)
    relationships = classifier.create_relationships()
    new_relationships = populate_relationships(relationships, term_set)

    flash("OntologyClassifier completed.")
    return render_template(
        "termset/list_relations.jinja", relationships=new_relationships
    )


@term.route("/set/relationships/<int:term_set_id>")
@login_required
def list_termset_relationships(term_set_id: int):
    term_set = TermSet.query.get_or_404(term_set_id)
    relationships = populate_relationships(term_set.relationships, term_set)

    return render_template("termset/list_relations.jinja", relationships=relationships)


@term.route("/set/classes/display/<int:term_set_id>")
def display_classes(term_set_id: int):
    term_set = TermSet.query.get_or_404(term_set_id)
    hierarchy_data = get_hierarchy_data(term_set_id)

    return render_template(
        "termset/display_classes.jinja", hierarchy=hierarchy_data, term_set=term_set
    )


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
