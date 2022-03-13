#!/usr/bin/env python
from datetime import datetime, timedelta
import unittest
from app import create_app, db
from app.user.models import User
from app.term.models import Term
from config import Config


class TestConfig(Config):
    TESTING = True
    DEBUG = True

    OAUTH_CREDENTIALS = {
        "google": {
            "id": "253843192125-vor93ruq7bqgrjp4u41iet9gv73qau6j.apps.googleusercontent.com",
            "secret": "mE1Xy4bqlNn4rOHpANGRV4h4",
        },
        "orcid": {
            "id": "APP-08MFGMT2OQULKN5J",
            "secret": "adfa3cbb-1268-4dcd-b623-5e932ca57ef1",
        },
    }

    OAUTH_URLS = {
        "orcid": {
            "authorize_url": "https://sandbox.orcid.org/oauth/authorize",
            "access_token_url": "https://sandbox.orcid.org/oauth/token",
            "base_url": "https://sandbox.orcid.org/v3.0/",
            "user_info_url": "https://api.sandbox.orcid.org/v3.0/{}/person",
        },
        "google": {
            "authorize_url": "https://accounts.google.com/o/oauth2/auth",
            "access_token_url": "https://accounts.google.com/o/oauth2/token",
            "base_url": "https://www.google.com/accounts/",
            "user_info_url": "https://www.googleapis.com/oauth2/v2/userinfo",
        },
    }
    SANDBOX = True


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


if __name__ == "__main__":
    unittest.main(verbosity=2)
