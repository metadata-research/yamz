from app import db

termset_relationships = db.Table(
    "termset_relationships",
    db.Column("relationship_id", db.Integer,
              db.ForeignKey("relationships.id")),
    db.Column("termset_id", db.Integer, db.ForeignKey("termsets.id")),

)
relationship_tags = db.Table(
    'relationship_tags',
    db.Column('relationship_id', db.Integer, db.ForeignKey(
        'relationships.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)
