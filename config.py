import os


class Config(object):
    # app
    SECRET_KEY = os.environ.get("SECRET_KEY") or "&HYa87yGR&ojKW3yJ&2bh#bQW"

    # database
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("SQL_ALCHEMY_DATABASE_URI")
        or "postgresql://postgres:PASS@localhost/seaice"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # oauth
    OAUTH_CREDENTIALS = {
        "google": {
            "id": "253843192125-vor93ruq7bqgrjp4u41iet9gv73qau6j.apps.googleusercontent.com",
            "secret": "96a07a50-3a0b-4342-8c12-79d7f83a1b4a",
        },
        "orcid": {
            "id": "APP-08MFGMT2OQULKN5J",
            "secret": "adfa3cbb-1268-4dcd-b623-5e932ca57ef1",
        },
    }


class TestConfig(Config):
    TESTING = True
    DEBUG = True
