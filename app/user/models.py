from app import db, login_manager
from flask_login import AnonymousUserMixin, UserMixin


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    __tablename__ = "users"
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
    last_message_read_time = db.Column(db.DateTime)

    # relationships
    terms = db.relationship(
        "Term", back_populates="contributor", order_by="Term.term_string"
    )

    tracking = db.relationship(
        "Track", back_populates="user", cascade="all, delete-orphan"
    )

    messages_sent = db.relationship(
        "Message",
        foreign_keys="Message.sender_id",
        back_populates="author",
        lazy="dynamic",
    )
    messages_received = db.relationship(
        "Message",
        foreign_keys="Message.recipient_id",
        back_populates="recipient",
        lazy="dynamic",
    )

    notifications = db.relationship("Notification", backref="user", lazy="dynamic")

    @property
    def is_administrator(self):
        return self.super_user

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return "<User: {}, {}>".format(self.last_name, self.first_name)


class AnonymousUser(AnonymousUserMixin):
    def is_administrator(self):
        return False

    def is_authenticated(self):
        return False
