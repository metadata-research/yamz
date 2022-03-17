import datetime
import json

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

    notifications = db.relationship(
        "Notification", back_populates="user", lazy="dynamic"
    )

    def add_notification(self, name, data):
        # self.notifications.filter_by(name=name).delete()
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        db.session.commit()
        # return n

    @property
    def new_message_count(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        count = (
            Message.query.filter_by(recipient=self)
            .filter(Message.timestamp > last_read_time)
            .count()
        )
        return str(count)

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


class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    recipient_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=db.func.now())
    sent = db.Column(db.Boolean, default=False)

    author = db.relationship(
        "User",
        back_populates="messages_sent",
        foreign_keys=[sender_id],
        lazy="joined",
    )
    recipient = db.relationship(
        "User",
        back_populates="messages_received",
        foreign_keys=[recipient_id],
        lazy="joined",
    )

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return "<Message {}>".format(self.body)


class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    timestamp = db.Column(db.DateTime, default=db.func.now())
    payload_json = db.Column(db.Text)

    user = db.relationship("User", back_populates="notifications", lazy="joined")

    def get_data(self):
        return json.loads(str(self.payload_json))
