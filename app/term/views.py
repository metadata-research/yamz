from flask import render_template
from app.term import term_blueprint as term
from app.term.models import Term


@term.route("/<concept_id>")  # change concelpt id to ark
def display_term(concept_id):

    # term = Term.query.filter_by(concept_id=concept_id).first()
    selected_term = Term.query.filter_by(concept_id=concept_id).first()
    return render_template("term/display_term.jinja", selected_term=selected_term)
