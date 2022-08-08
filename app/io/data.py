import pandas

from app.term.helpers import get_ark_id
from app import db
from flask import current_app
from app.term.models import Term
from flask_login import current_user

# pandas is a little overkill but we'll use it more later


def process_csv_upload(data_file):
    csv_dataframe = pandas.read_csv(data_file)
    return csv_dataframe.to_dict(orient="records")


def import_term_dict(term_dict):
    term_list = []
    for term in term_dict:
        term_string = term["term"]
        definition = term["definition"]
        examples = term["examples"]

        ark_id = get_ark_id()
        shoulder = current_app.config["SHOULDER"]
        naan = current_app.config["NAAN"]
        ark = shoulder + str(ark_id)
        owner_id = current_user.id

        new_term = Term(
            ark_id=ark_id,
            shoulder=shoulder,
            naan=naan,
            owner_id=owner_id,
            term_string=term_string,
            definition=definition,
            examples=examples,
            concept_id=ark,
        )
        db.session.add(new_term)
        db.session.commit()
        db.session.refresh(new_term)
        term_list.append(new_term)
    return term_list
