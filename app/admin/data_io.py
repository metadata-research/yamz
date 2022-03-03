import json, os, sys
from app.user.models import User
from app.term.models import Term, Track, Vote
from app import db

base_dir = os.path.abspath(os.path.dirname(__file__))


def add_users():
    # adds users with enotify as fals (default)
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
            sql = "ALTER SEQUENCE Users_id_seq RESTART WITH " + str(last_user_id + 1)
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
                    tsv=term["tsv"],
                )
                db.session.add(new_term)
                db.session.commit()
                print(term)
            else:
                print("Term already exists")


def transfer_tracking():
    file_path = os.path.join(base_dir, "json/tracking.json")
    with open(file_path, "r") as read_file:
        import_tracks = json.load(read_file)
        for track in import_tracks:
            track_user_id = track["user_id"]
            track_term_id = track["term_id"]
            vote = track["vote"]

            if not Track.query.filter_by(
                term_id=track_term_id, user_id=track_user_id
            ).first():
                # tracking
                if vote == track_user_id:
                    new_track = Track(term_id=track_term_id, user_id=track_user_id)
                    db.session.add(new_track)
                    db.session.commit()
                    print(new_track + "track added")
                # voting
                else:
                    new_vote = Vote(
                        term_id=track_term_id, user_id=track_user_id, vote=vote
                    )
                    db.session.add(new_vote)
                    db.session.commit()
                    print(new_vote + "vote  added")
            else:
                print("Track already exists")