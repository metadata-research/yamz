import re
import json
import os
import sys
import requests
from app.user.models import User
from app.term.models import Term, Track, Vote, Tag
from app import db
from app.admin.user import set_superuser
from app.term.helpers import get_ark_id
from flask import current_app
base_dir = os.path.abspath(os.path.dirname(__file__))


def add_users():
    # adds users with enotify as false (default)
    file_path = os.path.join(base_dir, "json/users.json")
    with open(file_path, "r") as read_file:
        import_users = json.load(read_file)
        for user in import_users:
            if not User.query.filter_by(id=user["id"]).first():
                new_user = User(
                    id=user["id"],
                    authority=user["authority"],
                    auth_id=user["auth_id"],
                    last_name=user["last_name"],
                    first_name=user["first_name"],
                    email=user["email"],
                    reputation=user["reputation"],
                    super_user=user["super_user"],
                )
                db.session.add(new_user)
                db.session.commit()
                print(user)
            else:
                print("User already exists")
    if not db.session.query(User.id).first() is None:
        last_user_id = db.session.query(db.func.max(User.id)).scalar()
        sql = "ALTER SEQUENCE Users_id_seq RESTART WITH " + \
            str(last_user_id + 1)
        db.session.execute(sql)
        db.session.commit()
        print("\nnext id:" + str(last_user_id + 1))


def add_terms():
    file_path = os.path.join(base_dir, "json/terms.json")
    with open(file_path, "r") as read_file:
        import_terms = json.load(read_file)
        for term in import_terms:
            if not Term.query.filter_by(id=term["id"]).first():
                new_term = Term(
                    id=term["id"],
                    ark_id=int(term["concept_id"][1:5]),
                    concept_id=term["concept_id"],
                    owner_id=term["owner_id"],
                    created=term["created"],
                    modified=term["modified"],
                    term_string=term["term_string"],
                    definition=term["definition"],
                    examples=term["examples"],
                    # tsv=term["tsv"],
                )
                db.session.add(new_term)
                db.session.commit()
                print(new_term)
            else:
                print("Term already exists")
    if not db.session.query(Term.id).first() is None:
        last_term_id = db.session.query(db.func.max(Term.id)).scalar()
        sql = "ALTER SEQUENCE Terms_id_seq RESTART WITH " + \
            str(last_term_id + 1)
        db.session.execute(sql)
        db.session.commit()
        print("\nnext id:" + str(last_term_id + 1))


def transfer_votes():
    file_path = os.path.join(base_dir, "json/tracking.json")
    with open(file_path, "r") as read_file:
        import_votes = json.load(read_file)
        for vote in import_votes:
            vote_user_id = vote["user_id"]
            vote_term_id = vote["term_id"]
            vote = vote["vote"]

            if vote_user_id == vote or vote == 0:
                print("This is a track, not a vote.")
            else:
                new_vote = Vote(term_id=vote_term_id,
                                user_id=vote_user_id, vote=vote)
                db.session.add(new_vote)
                db.session.commit()
                print(str(new_vote.user_id) + "vote  added")


def transfer_tracking():
    file_path = os.path.join(base_dir, "json/tracking.json")
    with open(file_path, "r") as read_file:
        import_tracks = json.load(read_file)
        for track in import_tracks:
            track_user_id = track["user_id"]
            track_term_id = track["term_id"]
            track = track["vote"]

            if track_user_id == track:
                new_track = Track(term_id=track_term_id, user_id=track_user_id)
                db.session.add(new_track)
                db.session.commit()
                print(str(new_track.user_id) + "track  added")


ref_regex = re.compile(
    "#\{\s*(([gstkm])\s*:+)?\s*([^}|]*?)(\s*\|+\s*([^}]*?))?\s*\}")
ixuniq = "xq"
ixqlen = len(ixuniq)
tagstart = "#{g: "  # note: final space is important


def transfer_tags():
    terms = Term.query.filter(Term.term_string.startswith("#"))
    count = 1
    for term in terms:
        start = term.term_string.find(ixuniq) + ixqlen
        end = term.term_string.rindex("|") - 1
        definition = term.definition
        new_tag = term.term_string
        new_tag = new_tag[start:end]
        if not Tag.query.filter_by(category="community", value=new_tag).first():
            tag = Tag(category="community", value=new_tag,
                      description=definition)
            tag.save()
            print("tag for " + tag.value + " added")
        else:
            print("Tag already exists")


###
###
###
# import and export functions
# python cli.py exportterms
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
        json.dump(export_terms, write_file, indent=4,
                  sort_keys=True, default=str)


def import_terms():
    file_path = os.path.join(base_dir, "export/terms.json")
    with open(file_path, "r") as read_file:
        import_terms = json.load(read_file)
        for term in import_terms:
            if not Term.query.filter_by(concept_id=term["concept_id"]).first():
                new_term = Term(
                    concept_id=term["concept_id"],
                    owner_id=term["owner_id"],
                    created=term["created"],
                    modified=term["modified"],
                    term_string=term["term_string"],
                    definition=term["definition"],
                    examples=term["examples"],
                    # tsv=term["tsv"],
                )
                db.session.add(new_term)
                db.session.commit()
                print(new_term)
            else:
                print("Term already exists")


def import_lcsh():
    lcsh = requests.get(
        'https://raw.githubusercontent.com/metadata-research/lcsh1910/main/LCSH1910-terms.txt?token=GHSAT0AAAAAACLANK7CKVLN7PJDSRC6VESUZLJACYA')
    lcsh = lcsh.text
    lcsh = lcsh.split("\n")

    lcsh_tag = Tag.query.filter_by(category="lcsh1910").first()
    if not lcsh_tag:
        lcsh_tag = Tag(category="lcsh1910", value="lcsh1910")
        lcsh_tag.save()

    # for term in lcsh:
    # add the first 5 terms
    for term_string in lcsh[:5]:
        print(term_string)
        # if there is not already a term with this term string and the tag lcsh1910, create one

        if not Term.query.filter(Term.term_string == term_string, Term.tags.contains(lcsh_tag)).first():
            ark_id = get_ark_id()
            shoulder = current_app.config["SHOULDER"]
            naan = current_app.config["NAAN"]
            ark = shoulder + str(ark_id)
            owner_id = 1

            new_term = Term(
                ark_id=ark_id,
                shoulder=shoulder,
                naan=naan,
                owner_id=owner_id,
                term_string=term_string,
                concept_id=ark,
            )

            db.session.add(new_term)
            new_term.tags.append(lcsh_tag)

            db.session.commit()
            print(new_term)
        else:
            print("Term already exists")
