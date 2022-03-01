from flask_login import AnonymousUserMixin, UserMixin
from app import db


class User(UserMixin, db.Model):
    __tablename__ = "users"
    __table_args__ = {"schema": "si"}
    # TODO: sequence
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    authority = db.Column(db.String(64), nullable=False)
    auth_id = db.Column(db.String(64), unique=True, nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    orcid = db.Column(db.String(64), nullable=True)
    reputation = db.Column(db.Integer, default=30)
    enotify = db.Column(db.Boolean, default=False)
    super_user = db.Column(db.Boolean, default=False)

    # relationships
    terms = db.relationship("Term", backref="contributor", lazy="dynamic")

    tracking = db.relationship(
        "Track", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )

    def save(self):
        db.session.add(self)
        db.session.commit()

    def is_tracking(self, term):
        if term.id is None:
            return False
        return self.tracking.filter_by(term_id=term.id).first() is not None

    @property
    def is_administrator(self):
        return self.super_user

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name

    def __repr__(self):
        return "<User: {}, {}>".format(self.last_name, self.first_name)


class AnonymousUser(AnonymousUserMixin):
    def is_administrator(self):
        return False
