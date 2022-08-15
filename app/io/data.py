import json
import os
from urllib import request

import pandas
from app import db
from app.term.helpers import get_ark_id
from app.term.models import Term
from app.user.models import User
from flask import current_app, make_response, request
from flask_login import current_user
from app.term.models import Term

base_dir = os.path.abspath(os.path.dirname(__file__))


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


def export_term_dict(search_terms=None):
    if search_terms is None:
        term_list = (
            db.session.query(Term)
            .with_entities(
                Term.id,
                Term.term_string,
                Term.definition,
                Term.examples,
                Term.ark_id,
                Term.owner_id,
            )
            .all()
        )
    else:
        term_list = (
            db.session.query(Term)
            .with_entities(
                Term.id,
                Term.term_string,
                Term.definition,
                Term.examples,
                Term.ark_id,
                Term.owner_id,
            )
            .filter(Term.__ts_vector__.match(search_terms))
            .all()
        )
    df_export_terms = pandas.DataFrame.from_records(
        term_list,
        columns=["id", "term_string", "definition", "examples", "ark_id", "owner_id"],
    )
    csv_list = df_export_terms.to_csv(index=False, header=True)
    output = make_response(csv_list)
    output.headers["Content-Disposition"] = "attachment; filename=terms.csv"
    output.headers["Content-Type"] = "text/csv"
    return output


def export_terms():
    file_path = os.path.join(base_dir, "export/terms.json")
    with open(file_path, "w") as write_file:
        terms = Term.query.all()
        export_terms = []
        for term in terms:
            owner_id = term.owner_id
            owner = User.query.filter_by(id=owner_id).first()
            export_terms.append(
                {
                    # "id": term.id,
                    "concept_id": term.concept_id,
                    "owner_id": owner_id,
                    "owner": owner,
                    "created": term.created,
                    "modified": term.modified,
                    "term_string": term.term_string,
                    "definition": term.definition,
                    "examples": term.examples,
                    # "tsv": term.tsv,
                }
            )
        json.dump(export_terms, write_file, indent=4, sort_keys=True, default=str)
