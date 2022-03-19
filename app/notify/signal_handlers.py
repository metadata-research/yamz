from app.term.models import term_saved, term_updated  # , term_deleted, term_commented
from flask import flash
from app import db


def term_to_json(term):
    return {
        "term": term.term_string,
        "term_id": term.id,
        "term_concept_id": term.concept_id,
    }


def term_updated_notify(term, **kwargs):
    user = term.contributor
    user.add_notification(
        "term_updated",
        term_to_json(term),
    )
    db.session.commit()

    flash(user.full_name + term.term_string + " updated")


def term_saved_notify(term, **kwargs):
    flash("Term saved <signal>")


def connect_handlers():
    term_saved.connect(term_saved_notify)
    term_updated.connect(term_updated_notify)
