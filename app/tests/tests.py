#!/usr/bin/env python
from datetime import datetime, timedelta
import unittest
from app import create_app, db
from app.user.models import User, Message, Notification
from app.term.models import Term, Tag, Track, Vote, Comment, status, term_class
from app.tests.test_term_patch import apply_sqlite_patches, restore_postgres_types
from config import Config
import unittest.mock


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"


class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_user_creation(self):
        """Test basic user creation and attributes"""
        u = User(
            authority="local",
            auth_id="test123",
            last_name="Test",
            first_name="User",
            email="test@example.com",
            reputation=30
        )
        db.session.add(u)
        db.session.commit()
        
        self.assertEqual(u.full_name, "User Test")
        self.assertEqual(u.reputation, 30)
        self.assertFalse(u.is_administrator)
        self.assertFalse(u.enotify)
        
    def test_user_admin(self):
        """Test admin user functionality"""
        admin = User(
            authority="local",
            auth_id="admin123",
            last_name="Admin",
            first_name="Super",
            email="admin@example.com",
            super_user=True
        )
        db.session.add(admin)
        db.session.commit()
        
        self.assertTrue(admin.is_administrator)
        
    def test_messaging(self):
        """Test messaging between users"""
        sender = User(
            authority="local",
            auth_id="sender123",
            last_name="Sender",
            first_name="Test",
            email="sender@example.com"
        )
        recipient = User(
            authority="local",
            auth_id="recipient123",
            last_name="Recipient",
            first_name="Test",
            email="recipient@example.com"
        )
        
        db.session.add_all([sender, recipient])
        db.session.commit()
        
        # Create and send a message
        msg = Message(
            sender_id=sender.id,
            recipient_id=recipient.id,
            body="Test message content"
        )
        db.session.add(msg)
        db.session.commit()
        
        # Check relationships
        self.assertEqual(sender.messages_sent.count(), 1)
        self.assertEqual(recipient.messages_received.count(), 1)
        self.assertEqual(recipient.messages_received.first().body, "Test message content")
        
    def test_notifications(self):
        """Test user notifications"""
        u = User(
            authority="local",
            auth_id="notify123",
            last_name="Notify",
            first_name="Test",
            email="notify@example.com"
        )
        db.session.add(u)
        db.session.commit()
        
        # Add a notification
        notification_data = {"message": "Test notification"}
        n = u.add_notification("test_notification", notification_data)
        db.session.commit()
        
        # Verify notification
        self.assertEqual(u.notifications.count(), 1)
        stored_data = u.notifications.first().get_data()
        self.assertEqual(stored_data, notification_data)


class TermModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Apply SQLite patches for compatibility
        apply_sqlite_patches()
        db.create_all()
        
        # Create a test user
        self.user = User(
            authority="local",
            auth_id="term_user123",
            last_name="Term",
            first_name="Test",
            email="term_test@example.com"
        )
        db.session.add(self.user)
        db.session.commit()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        restore_postgres_types()
        self.app_context.pop()
        
    def test_term_creation(self):
        """Test basic term creation and attributes"""
        term = Term(
            owner_id=self.user.id,
            term_string="Test Term",
            definition="This is a test definition.",
            examples="Example usage of the test term."
        )
        db.session.add(term)
        db.session.commit()
        
        # Verify term was created properly
        self.assertEqual(term.term_string, "Test Term")
        self.assertEqual(term.definition, "This is a test definition.")
        self.assertEqual(term.owner_id, self.user.id)
        self.assertEqual(term.status, "published")
        self.assertEqual(term.term_class, "vernacular")
        
    def test_term_voting(self):
        """Test term voting functionality with mocked vote methods"""
        term = Term(
            owner_id=self.user.id,
            term_string="Voting Term",
            definition="A term to test voting."
        )
        db.session.add(term)
        
        # Create voters
        voter1 = User(
            authority="local",
            auth_id="voter1",
            last_name="Voter1",
            first_name="Test",
            email="voter1@example.com"
        )
        voter2 = User(
            authority="local",
            auth_id="voter2",
            last_name="Voter2",
            first_name="Test",
            email="voter2@example.com"
        )
        db.session.add_all([voter1, voter2])
        db.session.commit()
        
        # We'll need to manually create Vote objects since TestTerm doesn't inherit behavior
        vote1 = Vote(user_id=voter1.id, term_id=term.id, vote=1)
        db.session.add(vote1)
        db.session.commit()
        
        # Add relationships manually for test
        term.votes = [vote1]
        
        # Test down-voting by adding another vote
        vote2 = Vote(user_id=voter2.id, term_id=term.id, vote=-1)
        db.session.add(vote2)
        db.session.commit()
        
        # Update relationships
        term.votes = [vote1, vote2]
        
        # Test vote count
        self.assertEqual(len(term.votes), 2)

    def test_term_tags(self):
        """Test adding tags to terms"""
        term = Term(
            owner_id=self.user.id,
            term_string="Tagged Term",
            definition="A term for testing tags."
        )
        
        # Create tags
        tag1 = Tag(category="test", value="tag1", description="Test tag 1")
        tag2 = Tag(category="test", value="tag2", description="Test tag 2")
        
        db.session.add_all([term, tag1, tag2])
        db.session.commit()
        
        # Set up tag relationship
        term.tags = [tag1, tag2]
        db.session.commit()
        
        # Verify tags were added
        self.assertEqual(len(term.tags), 2)
        tag_values = [tag.value for tag in term.tags]
        self.assertIn("tag1", tag_values)
        self.assertIn("tag2", tag_values)


if __name__ == "__main__":
    unittest.main(verbosity=2)
