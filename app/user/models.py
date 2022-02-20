import imp
from flask_login import AnonymousUserMixin, UserMixin
from app import db


class User(UserMixin, db.Model):
    # TODO: this is the legacy schema, use sqlalchemy.create_all() to create the tables and user the default naming conventions
    __tablename__ = "users"
    __table_args__ = {"schema": "si"}
    id = db.Column(db.Integer, primary_key=True)
    authority = db.Column(db.String(64))
    auth_id = db.Column(db.String(64), unique=True)
    last_name = db.Column(db.String(64))
    first_name = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True)
    orcid = db.Column(db.String(64), unique=True)
    reputation = db.Column(db.Integer)
    enotify = db.Column(db.Boolean)
    super_user = db.Column(db.Boolean)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def is_administrator(self):
        return self.super_user

    def __repr__(self):
        return "<User: {}, {}>".format(self.last_name, self.first_name)


class AnonymousUser(AnonymousUserMixin):
    def is_administrator(self):
        return False
