import os


class Config(object):
    # app
    SECRET_KEY = os.environ.get("SECRET_KEY") or "YOUR_SECRET_KEY"

    # database
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("SQL_ALCHEMY_DATABASE_URI")
        or "postgresql://postgres:PASS@localhost/yamz_prd"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # oauth
    OAUTH_CREDENTIALS = {
        "google": {
            "id": "YOUR_GOOGLE_API_ID.apps.googleusercontent.com",
            "secret": "YOUR_GOOGLE_API_SECRET",
        },
        "orcid": {
            "id": "APP-YOUR_ORCID_API_ID",
            "secret": "YOUR_ORCID_API_SECRET",
        },
    }

    OAUTH_URLS = {
        "orcid": {
            "authorize_url": "https://orcid.org/oauth/authorize",
            "access_token_url": "https://orcid.org/oauth/token",
            "base_url": "https://orcid.org/v3.0/",
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

    # ark related settings
    SHOULDER = "h"
    ARK_PREFIX = "ark:/99152/"
    NAAN = "YOUR_NAAN"

    # mail
    MAIL_SERVER = os.environ.get("MAIL_SERVER") or "smtp.mailgun.org"
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 587)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") or True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME") or "postmaster@mail.yamz.link"
    MAIL_PASSWORD = (
        os.environ.get("MAIL_PASSWORD")
        or "YOUR_MAILGUN_API_KEY"
    )
    ADMINS = ["ADMIN_EMAIL_ADDRESS"]

    # logging - set to True to see error messages on Flask console
    # set to False for public-facing service to capture messages in logs/...
    # files (directory and files will be created automatically)
    LOG_TO_STDOUT = True
