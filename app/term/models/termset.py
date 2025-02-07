
from app import db
from app.term.models.association_tables import termset_relationships

termset_tag_table = db.Table(
    "termset_tags",
    db.Column("termset_id", db.Integer, db.ForeignKey("termsets.id")),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id")),
)


class TermSet(db.Model):
    __tablename__ = "termsets"
    id = db.Column(db.Integer, primary_key=True)
    ark_id = db.Column(db.Integer, db.ForeignKey(
        "arks.id"), nullable=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    source = db.Column(db.Text)
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    created = db.Column(db.DateTime, default=db.func.now())
    updated = db.Column(db.DateTime, default=db.func.now(),
                        onupdate=db.func.now())

    terms = db.relationship(
        "Term",
        secondary="term_sets",
        back_populates="termsets",
        order_by="Term.term_string",
        single_parent=True,
        cascade="all, delete-orphan",
    )

    relationships = db.relationship(
        "Relationship",
        secondary=termset_relationships,
        back_populates="termsets",
    )

    ark = db.relationship("Ark", backref="termsets", uselist=False)

    tags = db.relationship(
        "Tag",
        secondary=termset_tag_table,
        back_populates="termsets",
    )

    @property
    def ark_concept_id(self):
        return self.ark.concept_id if self.ark else None

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
