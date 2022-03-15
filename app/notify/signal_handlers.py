from app.term.models import term_saved, term_updated  # , term_deleted, term_commented
from flask import flash


def term_updated_notify(term, **kwargs):
    flash("Term updated <signal>")


def term_saved_notify(term, **kwargs):
    flash("Term updated <signal>")


def connect_handlers():
    term_saved.connect(term_saved_notify)
    term_updated.connect(term_updated_notify)
