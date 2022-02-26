import enum
from unicodedata import name

from app import db
from sqlalchemy.dialects.postgresql import TSVECTOR

DB_SCHEMA = "si"


class si_class(enum.Enum):
    vernacular = (1, "vernacular")
    canonical = (2, "canonical")
    deprecated = (3, "deprecated")


class Term(db.Model):
    __tablename__ = "terms"
    __table_args__ = {"schema": DB_SCHEMA}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ark_id = db.Column(db.Integer, unique=True, autoincrement=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("si.users.id"))
    created = db.Column(db.DateTime, default=db.func.now())
    modified = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    term_string = db.Column(db.Text)
    definition = db.Column(db.Text)
    examples = db.Column(db.Text)
    concept_id = db.Column(db.String(64))
    persistent_id = db.Column(db.Text)  # make this always computed
    up = db.Column(db.Integer, default=0)
    down = db.Column(db.Integer, default=0)
    consensus = db.Column(db.Float, default=0)
    term_class = db.Column("class", db.Enum(si_class), default=si_class.vernacular)
    u_sum = db.Column(db.Integer, default=0)
    d_sum = db.Column(db.Integer, default=0)
    t_last = db.Column(db.DateTime)
    t_stable = db.Column(db.DateTime)
    tsv = db.Column(TSVECTOR)

    # relationships
    tracks = db.relationship("Track", backref="term", lazy="dynamic")

    votes = db.relationship(
        "Vote", backref="term", lazy="dynamic", cascade="all, delete-orphan"
    )

    comments = db.relationship("Comment", backref="term", lazy="dynamic")

    @property
    def vote_total(self):
        votes = self.votes
        vote_sum = 0
        for vote in votes:
            vote_sum += vote.vote
        return vote_sum

    def get_user_vote(self, current_user):
        # return lambda self, current_user: self.votes.filter_by(
        #    user_id=current_user.id
        # ).first()
        user_vote = self.votes.filter_by(user_id=current_user.id).first()
        return user_vote.vote if user_vote else 0

    @property
    def score(self):
        return self.up - self.down

    @property
    def alt_definitions_count(self):
        return (
            db.session.query(db.func.count(Term.id))
            .filter_by(term_string=self.term_string)
            .filter(Term.id != self.id)
            .scalar()
        )

    def save(self):
        db.session.add(self)
        db.session.commit()

    def track(self, current_user):
        if not self.tracks.filter_by(user_id=current_user.id).first():
            track = Track(user_id=current_user.id, term_id=self.id)
            track.save()

    def untrack(self, current_user):
        if self.tracks.filter_by(user_id=current_user.id).first():
            untrack = self.tracks.filter_by(user_id=current_user.id).first()
            db.session.delete(untrack)
            db.session.commit()

    def up_vote(self, current_user):
        vote = self.votes.filter_by(user_id=current_user.id).first()
        if vote is None:
            vote = Vote(user_id=current_user.id, term_id=self.id, vote=1)
        elif vote.vote == 1:
            return False
        else:
            vote.vote = 1
        vote.save()

    def down_vote(self, current_user):
        vote = self.votes.filter_by(user_id=current_user.id).first()
        if vote is None:
            vote = Vote(user_id=current_user.id, term_id=self.id, vote=-1)
        elif vote.vote == -1:
            return False
        else:
            vote.vote = -1
        vote.save()

    def zero_vote(self, current_user):
        vote = self.votes.filter_by(user_id=current_user.id).first()
        if vote is None:
            vote = Vote(user_id=current_user.id, term_id=self.id, vote=0)
        else:
            vote.vote = 0
        vote.save()


class Comment(db.Model):
    __tablename__ = "comments"
    __table_args__ = {"schema": DB_SCHEMA}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("si.users.id"))
    term_id = db.Column(db.Integer, db.ForeignKey("si.terms.id"))
    created = db.Column(db.DateTime, default=db.func.now())
    modified = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    comment_string = db.Column(db.Text)

    author = db.relationship("User", backref="author", lazy="joined")

    def save(self):
        db.session.add(self)
        db.session.commit()


class Track(db.Model):
    __tablename__ = "tracking"
    __table_args__ = {"schema": DB_SCHEMA}
    user_id = db.Column(db.Integer, db.ForeignKey("si.users.id"), primary_key=True)
    term_id = db.Column(db.Integer, db.ForeignKey("si.terms.id"), primary_key=True)
    vote = db.Column(db.Integer, default=0)
    star = db.Column(db.Boolean, default=False)

    def save(self):
        db.session.add(self)
        db.session.commit()


class Vote(db.Model):
    __tablename__ = "votes"
    __table_args__ = {"schema": DB_SCHEMA}
    user_id = db.Column(db.Integer, db.ForeignKey("si.users.id"), primary_key=True)
    term_id = db.Column(db.Integer, db.ForeignKey("si.terms.id"), primary_key=True)
    vote = db.Column(db.Integer, default=0, nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()
