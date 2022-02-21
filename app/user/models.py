from typing import Sequence
from flask_login import AnonymousUserMixin, UserMixin
from app import db


class User(UserMixin, db.Model):
    __tablename__ = "users"
    __table_args__ = {"schema": "si"}
    # TODO: sequence
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    authority = db.Column(db.String(64))
    auth_id = db.Column(db.String(64), unique=True)
    last_name = db.Column(db.String(64))
    first_name = db.Column(db.String(64))
    email = db.Column(db.String(64))
    orcid = db.Column(db.String(64), unique=True)
    reputation = db.Column(db.Integer, default=30)
    enotify = db.Column(db.Boolean, default=False)
    super_user = db.Column(db.Boolean, default=False)

    # terms = db.relationship("Term", backref="author", lazy="dynamic")

    def save(self):
        db.session.add(self)
        db.session.commit()

    @property
    def is_administrator(self):
        return self.super_user

    def __repr__(self):
        return "<User: {}, {}>".format(self.last_name, self.first_name)


class AnonymousUser(AnonymousUserMixin):
    def is_administrator(self):
        return False
