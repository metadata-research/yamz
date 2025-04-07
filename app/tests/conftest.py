import pytest
from app import create_app, db
from app.user.models import User
from app.term.models import Term, Tag, Track, Vote, Comment, status, term_class
from app.tests.test_term_patch import apply_sqlite_patches, restore_postgres_types
from config import Config
import unittest.mock


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
        return user


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
        return admin


@pytest.fixture
def test_term(app, test_user):
    """Create a test term."""
    with app.app_context():
        term = Term(
            owner_id=test_user.id,
            term_string="PyTest Term",
            definition="A term created for pytest."
        )
        db.session.add(term)
        db.session.commit()
        return term
