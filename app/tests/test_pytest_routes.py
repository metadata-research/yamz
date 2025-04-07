import pytest
from flask import url_for
import unittest.mock
from app.tests.test_models import TestTerm


def test_home_page(client):
    """Test that the home page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    # Check for expected content
    assert b'YAMZ' in response.data


def test_about_page(client):
    """Test that the about page loads correctly."""
    response = client.get('/about')
    assert response.status_code == 200


def test_term_page(client, test_term):
    """Test that a term page loads correctly."""
    response = client.get(f'/term/{test_term.id}')
    assert response.status_code == 200
    # Check that the term string is in the response
    assert test_term.term_string.encode() in response.data
    # Check that the definition is in the response
    assert test_term.definition.encode() in response.data


def test_nonexistent_term(client):
    """Test accessing a nonexistent term."""
    # Using a very large ID that probably doesn't exist
    response = client.get('/term/999999')
    assert response.status_code == 404


def test_login_page(client):
    """Test that the login page loads correctly."""
    response = client.get('/login')
    assert response.status_code == 200
    # Check for login-related content
    assert b'login' in response.data.lower()


def test_terms_list_page(client, test_term):
    """Test that the terms list page loads correctly."""
    response = client.get('/term/list')
    assert response.status_code == 200
    # The term we created should be in the list
    assert test_term.term_string.encode() in response.data


def test_user_profile_unauthenticated(client, test_user):
    """Test accessing a user profile when not logged in."""
    response = client.get(f'/user/{test_user.id}')
    # Either redirects to login or shows the profile with limited info
    assert response.status_code in [200, 302]


def test_search_functionality(client, test_term):
    """Test the search functionality."""
    # Search for a term
    response = client.get(f'/term/search?q={test_term.term_string}')
    assert response.status_code == 200
    # The search results should contain our test term
    assert test_term.term_string.encode() in response.data
