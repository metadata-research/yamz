import json, os, sys
from app.user.models import User
from app import db

base_dir = os.path.abspath(os.path.dirname(__file__))
file_path = os.path.join(base_dir, "json/users.json")


def print_users():
    # file_path = "/static/json/users.json"
    with open(file_path, "r") as read_file:
        import_users = json.load(read_file)
        for user in import_users:
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
