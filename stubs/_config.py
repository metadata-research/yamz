import os


class Config(object):
    # app
    SECRET_KEY = os.environ.get("SECRET_KEY") or "<your-secret-key>"

    # database
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("SQL_ALCHEMY_DATABASE_URI")
        or "postgresql://postgres:PASS@localhost/yamz"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # oauth
    OAUTH_CREDENTIALS = {
        "google": {
            "id": "<your-client-id>",
            "secret": "<your-client-secret>",
        },
        "orcid": {
            "id": "<your-client-id>",
            "secret": "<your-client-secret>",
        },
    }

    OAUTH_URLS = {
        "orcid": {
            "authorize_url": "https://orcid.org/oauth/authorize",
            "access_token_url": "https://orcid.org/oauth/token",
            "base_url": "https://orcid.org/",
            "user_info_url": "https://pub.orcid.org/3.0/{}/person",
        },
        "google": {
            "authorize_url": "https://accounts.google.com/o/oauth2/auth",
            "access_token_url": "https://accounts.google.com/o/oauth2/token",
            "base_url": "https://www.google.com/accounts/",
            "user_info_url": "https://www.googleapis.com/oauth2/v2/userinfo",
        },
    }

    # misc
    SANDBOX = False
    TERMS_PER_PAGE = 20

    # ark realted settings
    SHOULDER = "h"
    ARK_PREFIX = "ark:/99152/"


class TestConfig(Config):
    TESTING = True
    DEBUG = True

    OAUTH_URLS = {
        "orcid": {
            "authorize_url": "https://sandbox.orcid.org/oauth/authorize",
            "access_token_url": "https://sandbox.orcid.org/oauth/token",
            "base_url": "https://sandbox.orcid.org/",
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
