#!/usr/bin/env python
import unittest
from app import create_app, db
from app.term.models import Term
from app.user.models import User
from app.tests.test_term_patch import apply_sqlite_patches, restore_postgres_types
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"

class DebugRouteTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        apply_sqlite_patches()
        db.create_all()
        
        # Create user
        self.user = User(
            authority="local",
            auth_id="debug_user",
            last_name="Debug",
            first_name="User",
            email="debug@example.com"
        )
        db.session.add(self.user)
        
        # Create term
        self.term = Term(
            owner_id=self.user.id,
            term_string="Debug Term",
            definition="Term for debugging"
        )
        db.session.add(self.term)
        db.session.commit()
        
        print(f"Created term with ID: {self.term.id}")
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        restore_postgres_types()
        self.app_context.pop()
    
    def test_term_page(self):
        """Test that a term page loads correctly"""
        # Test term page access
        url = f'/term/{self.term.id}'
        print(f"Testing URL: {url}")
        response = self.client.get(url)
        print(f"Response status: {response.status_code}")
        
        # Debug output to see what's in the response
        if response.status_code != 200:
            print(f"URL not found: {url}")
            
            # Test if other URLs work
            home = self.client.get('/')
            print(f"Home page status: {home.status_code}")
            
            # Check if term exists in DB after setup
            term_check = Term.query.get(self.term.id)
            print(f"Term in DB: {term_check is not None}")
            if term_check:
                print(f"Term string: {term_check.term_string}")
        
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
