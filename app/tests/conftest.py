import pytest
from app import create_app, db
from app.user.models import User
from app.term.models import Term, Tag, Track, Vote, Comment, status, term_class
from sqlalchemy import String, Column
from sqlalchemy.dialects.postgresql import TSVECTOR
from config import Config
import unittest.mock

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


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app(TestConfig)
    
    # Create the database and the database tables
    with app.app_context():
        # Apply SQLite-compatible patches
        apply_sqlite_patches()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        # Restore original types
        restore_postgres_types()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(
            authority="local",
            auth_id="pytest_user123",
            last_name="PyTest",
            first_name="User",
            email="pytest_user@example.com"
        )
        db.session.add(user)
        db.session.commit()
        # Get the user id to use later
        user_id = user.id
        db.session.close()
        
        # Create a new session for each test
        user = db.session.get(User, user_id)
        yield user
        db.session.close()


@pytest.fixture
def admin_user(app):
    """Create an admin user."""
    with app.app_context():
        admin = User(
            authority="local",
            auth_id="pytest_admin123",
            last_name="PyTest",
            first_name="Admin",
            email="pytest_admin@example.com",
            super_user=True
        )
        db.session.add(admin)
        db.session.commit()
        # Get the admin id to use later
        admin_id = admin.id
        db.session.close()
        
        # Create a new session for each test
        admin = db.session.get(User, admin_id)
        yield admin
        db.session.close()


@pytest.fixture
def test_term(app, test_user):
    """Create a test term."""
    with app.app_context():
        # Ensure test_user is attached to the current session
        term = Term(
            owner_id=test_user.id,
            term_string="PyTest Term",
            definition="A term created for pytest."
        )
        db.session.add(term)
        db.session.commit()
        # Get the term id to use later
        term_id = term.id
        db.session.close()
        
        # Create a new session for each test
        term = db.session.get(Term, term_id)
        yield term
        db.session.close()
