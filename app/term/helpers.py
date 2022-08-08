from app import db
from app.term.models import Term


def get_ark_id():
    ark_id = db.session.query(db.func.max(Term.ark_id)).scalar()
    if ark_id is None:
        ark_id = 0
    return ark_id + 1
