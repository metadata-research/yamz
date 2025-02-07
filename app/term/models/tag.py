from app import db
from .termset import termset_tag_table
from app.term.models.association_tables import relationship_tags


class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    category = db.Column(db.Text, default="user")
    value = db.Column(db.Text)
    description = db.Column(db.Text)
    domain = db.Column(db.Text)

    terms = db.relationship(
        "Term",
        secondary="term_tags",
        back_populates="tags",
        order_by="Term.term_string",
    )

    termsets = db.relationship(
        "TermSet",
        secondary=termset_tag_table,
        back_populates="tags",
    )

    relationships = db.relationship(
        "Relationship", secondary=relationship_tags, back_populates="tags")

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    #    def __init__(self, *args, **kwargs):
    #        super(Tag, self).__init__(*args, **kwargs)
    #        self.reference = normalize_tag(self.name + "#" + self.value)

    def __repr__(self):
        return "<Tag {} {}>".format(self.category, self.value)
