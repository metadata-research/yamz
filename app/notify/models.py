import json
from app import db


class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    recipient_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=db.func.now())

    def __repr__(self):
        return "<Message {}>".format(self.body)


class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    timestamp = db.Column(db.Float, index=True, default=db.func.now())
    payload_json = db.Column(db.Text)

    def get_data(self):
        return json.loads(str(self.payload_json))
