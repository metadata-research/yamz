#!/usr/bin/env python
import unittest
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


class RoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        # Apply SQLite patches for compatibility
        apply_sqlite_patches()
        db.create_all()
        
        # Create test user
        self.test_user = User(
            authority="local",
            auth_id="route_test123",
            last_name="Route",
            first_name="Test",
            email="route_test@example.com"
        )
        db.session.add(self.test_user)
        
        # Create test term - use the actual user ID instead of hardcoding to 1
        self.test_term = Term(
            owner_id=self.test_user.id,
            term_string="Test Route Term",
            definition="A term for testing routes."
        )
        db.session.add(self.test_term)
        db.session.commit()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        restore_postgres_types()
        self.app_context.pop()
    
    def test_home_page(self):
        """Test that the home page loads"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
    def test_term_page(self):
        """Test that a term's page loads"""
        response = self.client.get(f'/term/{self.test_term.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Route Term', response.data)
        
    def test_nonexistent_term(self):
        """Test accessing a term that doesn't exist"""
        response = self.client.get('/term/99999')  # Assuming this ID doesn't exist
        self.assertEqual(response.status_code, 404)
        
    def test_about_page(self):
        """Test that the about page loads"""
        response = self.client.get('/about')
        self.assertEqual(response.status_code, 200)
        
    def test_login_page(self):
        """Test that the login page loads"""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main(verbosity=2)
