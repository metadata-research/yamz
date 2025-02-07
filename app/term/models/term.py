import enum
import re
from sqlalchemy import Index, select, case
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.ext.hybrid import hybrid_property
from markdown import markdown
import bleach
from blinker import Namespace

from app import db
from app.term.models.track import Track
from app.user.models import User
from config import Config

# Constants
SHOULDER = Config.SHOULDER
NAAN = Config.NAAN
ALLOWED_TAGS = [
    "a", "abbr", "acronym", "b", "blockquote", "code", "em", "i", "li",
    "ol", "pre", "strong", "ul", "h1", "h2", "h3", "p"
]

# Helper Functions
def normalize_tag(reference):
    """Normalize a string to create a tag."""
    return re.sub(r"[^\w]+", "-", reference).lower()


# Enumerations
class TermClass(enum.Enum):
    vernacular = (1, "vernacular")
    canonical = (2, "canonical")
    deprecated = (3, "deprecated")


class Status(enum.Enum):
    archived = (1, "archived")
    published = (2, "published")
    draft = (3, "draft")
    deleted = (4, "deleted")


# Models
class Term(db.Model):
    __tablename__ = "terms"

    # Columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ark_id = db.Column(db.Integer, unique=True, autoincrement=True)
    shoulder = db.Column(db.String(64), default=SHOULDER)
    naan = db.Column(db.String(64), default=NAAN)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created = db.Column(db.DateTime, default=db.func.now())
    modified = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    term_string = db.Column(db.Text)
    definition = db.Column(db.Text)
    definition_html = db.Column(db.Text)
    examples = db.Column(db.Text)
    examples_html = db.Column(db.Text)
    concept_id = db.Column(db.String(64))
    status = db.Column("status", db.Enum(Status), default=Status.published)
    term_class = db.Column("class", db.Enum(TermClass), default=TermClass.vernacular)
    search_vector = db.Column(TSVECTOR)

    __table_args__ = (
        Index("ix_term_search_vector", search_vector, postgresql_using="gin"),
    )

    # Relationships
    termsets = db.relationship(
        "TermSet", secondary="term_sets", back_populates="terms", cascade="all"
    )
    contributor = db.relationship("User", back_populates="terms")
    tags = db.relationship("Tag", secondary="term_tags", back_populates="terms")
    tracks = db.relationship("Track", back_populates="term", cascade="all, delete-orphan")
    votes = db.relationship("Vote", backref="term", lazy="dynamic", cascade="all, delete-orphan")
    comments = db.relationship("Comment", backref="term", lazy="dynamic")

    # Properties and Methods
    @property
    def persistent_id(self):
        return f"https://n2t.net/ark:/{self.naan}/{self.shoulder}{self.ark_id}"

    @hybrid_property
    def term_vote(self):
        return sum(vote.vote for vote in self.votes)

    @term_vote.expression
    def term_vote(cls):
        return select([db.func.sum(Vote.vote)]).where(Vote.term_id == cls.id)

    def get_user_vote(self, current_user):
        vote = self.votes.filter_by(user_id=current_user.id).first()
        return vote.vote if vote else 0

    @property
    def alt_definitions_count(self):
        return db.session.query(db.func.count(Term.id)).filter(
            Term.term_string == self.term_string, Term.id != self.id
        ).scalar()

    def is_tracked_by(self, current_user):
        return any(track.user.id == current_user.id for track in self.tracks)

    def update_search_vector(self):
        tags = " ".join(tag.value for tag in self.tags) if self.tags else ""
        text = f"{self.definition or ''} {self.examples or ''} {tags}".strip()
        self.search_vector = db.func.to_tsvector("english", text)

    def save(self):
        self.update_search_vector()
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f"<Term {self.term_string} | {self.concept_id}>"


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    term_id = db.Column(db.Integer, db.ForeignKey("terms.id"))
    created = db.Column(db.DateTime, default=db.func.now())
    modified = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    comment_string = db.Column(db.Text)
    comment_string_html = db.Column(db.Text)

    author = db.relationship("User", backref="author", lazy="joined")

    @staticmethod
    def clean_html(value):
        return bleach.linkify(bleach.clean(markdown(value, output_format="html"), tags=ALLOWED_TAGS, strip=True))

    def save(self):
        self.comment_string_html = self.clean_html(self.comment_string)
        db.session.add(self)
        db.session.commit()


class Vote(db.Model):
    __tablename__ = "votes"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    term_id = db.Column(db.Integer, db.ForeignKey("terms.id"), primary_key=True)
    vote = db.Column(db.Integer, default=0, nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()


# Association Tables
tag_table = db.Table(
    "term_tags",
    db.Model.metadata,
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id")),
    db.Column("term_id", db.Integer, db.ForeignKey("terms.id")),
)

set_table = db.Table(
    "term_sets",
    db.Model.metadata,
    db.Column("set_id", db.Integer, db.ForeignKey("termsets.id")),
    db.Column("term_id", db.Integer, db.ForeignKey("terms.id")),
)


# Signals
term_signals = Namespace()
term_saved = term_signals.signal("term_saved")
term_deleted = term_signals.signal("term_deleted")
term_updated = term_signals.signal("term_updated")
term_commented = term_signals.signal("term_commented")
term_tracked = term_signals.signal("term_tracked")
term_voted = term_signals.signal("term_voted")
