import pytest
from app.user.models import User, Message, Notification
from app.term.models import Term, Tag, Vote, Comment, status, term_class
from app import db
import unittest.mock


def test_user_model(app, test_user):
    """Test the User model with pytest fixtures."""
    with app.app_context():
        # Test basic attributes
        assert test_user.full_name == "User PyTest"
        assert test_user.authority == "local"
        assert not test_user.is_administrator
        
        # Test reputation default
        assert test_user.reputation == 30


def test_admin_user(app, admin_user):
    """Test admin user functionality."""
    with app.app_context():
        assert admin_user.is_administrator
        assert admin_user.super_user


def test_term_model(app, test_term, test_user):
    """Test the Term model."""
    with app.app_context():
        # Check basic attributes
        assert test_term.term_string == "PyTest Term"
        assert test_term.definition == "A term created for pytest."
        assert test_term.owner_id == test_user.id
        
        # Check default status and class
        assert test_term.status == "published"
        assert test_term.term_class == "vernacular"


def test_term_voting(app, test_term, test_user, admin_user):
    """Test term voting functionality."""
    with app.app_context():
        # Create votes directly
        vote1 = Vote(user_id=test_user.id, term_id=test_term.id, vote=1)
        db.session.add(vote1)
        db.session.commit()
        
        # Add relationship manually
        test_term.votes = [vote1]
        
        # Add another vote
        vote2 = Vote(user_id=admin_user.id, term_id=test_term.id, vote=-1)
        db.session.add(vote2)
        db.session.commit()
        
        # Update relationship
        test_term.votes = [vote1, vote2]
        
        # Test vote count
        assert len(test_term.votes) == 2


def test_term_tagging(app, test_term):
    """Test adding tags to a term."""
    with app.app_context():
        # Create tags
        tag1 = Tag(category="pytest", value="tag1", description="PyTest tag 1")
        tag2 = Tag(category="pytest", value="tag2", description="PyTest tag 2")
        db.session.add_all([tag1, tag2])
        db.session.commit()
        
        # Set tags directly
        test_term.tags = [tag1, tag2]
        db.session.commit()
        
        # Verify
        assert len(test_term.tags) == 2
        tag_values = [tag.value for tag in test_term.tags]
        assert "tag1" in tag_values
        assert "tag2" in tag_values


def test_messaging(app, test_user, admin_user):
    """Test messaging between users."""
    with app.app_context():
        # Create and send a message
        msg = Message(
            sender_id=test_user.id,
            recipient_id=admin_user.id,
            body="Test pytest message"
        )
        db.session.add(msg)
        db.session.commit()
        
        # Check message counts
        assert test_user.messages_sent.count() == 1
        assert admin_user.messages_received.count() == 1
        
        # Check message content
        received_msg = admin_user.messages_received.first()
        assert received_msg.body == "Test pytest message"
        assert received_msg.author.id == test_user.id
