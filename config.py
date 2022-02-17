import os


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "!yamz-development-secret-key#"
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:PASS@localhost/seaice"

    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "postgresql://"
