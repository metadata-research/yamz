"""
Patches for SQLite compatibility in tests
"""
from sqlalchemy import String, Column
from sqlalchemy.dialects.postgresql import TSVECTOR
from app.term.models import Term

# Save the original TSVECTOR column
original_search_vector = Term.__table__.columns['search_vector']

def apply_sqlite_patches():
    """
    Patch PostgreSQL-specific types to work with SQLite for testing
    """
    # Replace TSVECTOR with String for SQLite compatibility
    Term.__table__.columns['search_vector'].type = String()
    # Mark the column as not being constrained for CREATE TABLE
    Term.__table__.columns['search_vector'].primary_key = False
    Term.__table__.columns['search_vector'].nullable = True
    Term.__table__.columns['search_vector'].constraints = set()
    
    # Note: we're modifying the Term class directly, which will affect all 
    # tests that use this class. This is fine for testing purposes.
    return True

def restore_postgres_types():
    """
    Restore original PostgreSQL types after tests
    """
    Term.__table__.columns['search_vector'].type = original_search_vector.type
    Term.__table__.columns['search_vector'].primary_key = original_search_vector.primary_key
    Term.__table__.columns['search_vector'].nullable = original_search_vector.nullable
    Term.__table__.columns['search_vector'].constraints = original_search_vector.constraints
    return True
