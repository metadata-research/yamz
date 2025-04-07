"""
Custom model definitions for testing
"""
from sqlalchemy.ext.declarative import declared_attr
from app.term.models import Term as ProductionTerm
from app import db
from sqlalchemy import Column, String


class TestTerm(db.Model):
    """
    Modified Term model for testing that skips the PostgreSQL-specific TSVECTOR column
    """
    __tablename__ = "test_terms"

    # Copy all columns from ProductionTerm
    id = Column(db.Integer, primary_key=True, autoincrement=True)
    ark_id = Column(db.Integer, unique=True, autoincrement=True)
    shoulder = Column(db.String(64), default="h")
    naan = Column(db.String(64), default="99152")
    owner_id = Column(db.Integer, db.ForeignKey("users.id"))
    created = Column(db.DateTime, default=db.func.now())
    modified = Column(db.DateTime, default=db.func.now(),
                     onupdate=db.func.now())
    term_string = Column(db.Text)
    definition = Column(db.Text)
    definition_html = Column(db.Text)
    examples = Column(db.Text)
    examples_html = Column(db.Text)
    concept_id = Column(db.String(64))
    # Use string values for enum types in tests rather than the enum objects
    status = Column("status", db.Enum("archived", "published", "draft", "deleted", 
                                     name="status"),
                   default="published")
    term_class = Column("class", db.Enum("vernacular", "canonical", "deprecated", 
                                        name="term_class"),
                       default="vernacular")
    
    # Skip the TSVECTOR column and associated index

    # Add a dummy search_vector for compatibility with methods that use it
    search_vector = Column(String, default="")

    # Define minimal relationships for tests - actual relationships will be set manually in tests
    votes = db.relationship("Vote")
    tags = db.relationship("Tag", secondary="term_tags")
    comments = db.relationship("Comment")
    contributor = db.relationship("User", foreign_keys=[owner_id])
