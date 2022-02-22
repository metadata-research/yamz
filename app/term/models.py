from unicodedata import name
from app import db
from sqlalchemy.dialects.postgresql import TSVECTOR
import enum


class si_class(enum.Enum):
    vernacular = ("vernacular",)
    canonical = ("canonical",)
    depricated = ("depricated",)


class Term(db.Model):
    __tablename__ = "terms"
    __table_args__ = {"schema": "si"}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ark_id = db.Column(db.Integer, unique=True, autoincrement=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("si.users.id"))
    created = db.Column(db.DateTime, default=db.func.now())
    modified = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    term_string = db.Column(db.Text)
    definition = db.Column(db.Text)
    examples = db.Column(db.Text)
    concept_id = db.Column(db.String(64))
    persistent_id = db.Column(db.Text)
    up = db.Column(db.Integer, default=0)
    down = db.Column(db.Integer, default=0)
    consensus = db.Column(db.Float, default=0)
    si_class = db.Column("class", db.Enum(si_class), default=si_class.vernacular)
    u_sum = db.Column(db.Integer, default=0)
    d_sum = db.Column(db.Integer, default=0)
    t_last = db.Column(db.DateTime)
    t_stable = db.Column(db.DateTime)
    tsv = db.Column(TSVECTOR)

    @property
    def score(self):
        return self.up - self.down

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return "<Term %r>" % self.term_string
