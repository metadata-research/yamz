from app.user.models import User
from app import db


def set_superuser(email):
    user = User.query.filter_by(email=email).first()
    if user:
        user.super_user = True
        db.session.commit()
        print("User " + email + " is now a superuser")
    else:
        print("User " + email + " does not exist")
