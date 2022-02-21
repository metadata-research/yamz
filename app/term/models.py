from app import db


class Term(db.Model):
    __tablename__ = "terms"
    __table_args__ = {"schema": "si"}
    id = db.Column(db.Integer, primary_key=True)
