from app.term.models import term_saved, term_updated, term_tracked  # , term_deleted, term_commented
from flask import flash
from app import db


def term_to_json(term):
    return {
        "term_string": term.term_string,
        "term_id": term.id,
        "term_concept_id": term.concept_id,
    }


def notify_users(term):
    users_to_notify = []
    users_to_notify.append(term.contributor)
    
    for track in term.tracks:
        if track.user not in users_to_notify:
            users_to_notify.append(track.user)
    
    return users_to_notify

def term_updated_notify(term, **kwargs):
    users_to_notify = notify_users(term)
     
    for user in users_to_notify:
        user.add_notification(
            "Term Updated",
            term_to_json(term),
        )
        db.session.commit()

def term_saved_notify(term, **kwargs):
    flash("Term saved (from signal)")


def term_tracked_notify(term, **kwargs):
    users_to_notify = notify_users(term)
     
    for user in users_to_notify:
        user.add_notification(
            "Term Watched",
            term_to_json(term),
        )
        db.session.commit()

def connect_handlers():
    term_saved.connect(term_saved_notify)
    term_updated.connect(term_updated_notify)
    term_tracked.connect(term_tracked_notify)