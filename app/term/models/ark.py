from app import db
from config import Config
from sqlalchemy.orm import column_property
from sqlalchemy import func, Sequence

SHOULDER = Config.SHOULDER
NAAN = Config.NAAN

ark_id_seq = Sequence('ark_id_seq', start=1000)


class Ark(db.Model):
    __tablename__ = "arks"
    id = db.Column(db.Integer, primary_key=True)
    ark_id = db.Column(db.Integer, unique=True,
                       server_default=db.FetchedValue())
    shoulder = db.Column(db.String(64), default=SHOULDER)
    naan = db.Column(db.String(64), default=NAAN)
    created = db.Column(db.DateTime, default=db.func.now())
    modified = db.Column(db.DateTime, default=db.func.now(),
                         onupdate=db.func.now())
    concept_id = column_property(func.concat(shoulder, ark_id))

    @classmethod
    def create_ark(cls, shoulder=None, naan=None):
        if shoulder is None:
            shoulder = SHOULDER
        if naan is None:
            naan = NAAN

        # Get the next value from the sequence
        next_ark_id_value = db.session.execute(ark_id_seq)

        # Create a new Ark instance with the next ark_id
        new_ark = cls(shoulder=shoulder, naan=naan, ark_id=next_ark_id_value)
        db.session.add(new_ark)
        db.session.commit()
        return new_ark

    @property
    def full_ark(self):
        return f"{self.naan}/{self.shoulder}{self.ark_id}"

    def __repr__(self):
        return f"<Ark {self.shoulder}{self.ark_id}>"
