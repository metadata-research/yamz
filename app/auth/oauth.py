import json

# import orcid

from flask import current_app, url_for, redirect, request
from rauth import OAuth2Service


class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = current_app.config["OAUTH_CREDENTIALS"][provider_name]
        self.consumer_id = credentials["id"]
        self.consumer_secret = credentials["secret"]

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self):
        return url_for(
            "auth.oauth_callback", provider=self.provider_name, _external=True
        )

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]


class GoogleSignIn(OAuthSignIn):
    def __init__(self):
        super(GoogleSignIn, self).__init__("google")
        self.service = OAuth2Service(
            name="google",
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url="https://accounts.google.com/o/oauth2/auth",
            access_token_url="https://accounts.google.com/o/oauth2/token",
            base_url="https://www.google.com/accounts/",
        )

    def authorize(self):
        return redirect(
            self.service.get_authorize_url(
                scope="profile email",
                response_type="code",
                redirect_uri=self.get_callback_url(),
            )
        )

    def callback(self):
        def decode_json(payload):
            return json.loads(payload.decode("utf-8"))

        if "code" not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            data={
                "code": request.args["code"],
                "grant_type": "authorization_code",
                "redirect_uri": self.get_callback_url(),
            },
            decoder=decode_json,
        )
        me = oauth_session.get("https://www.googleapis.com/oauth2/v2/userinfo").json()

        return (
            me.get("id"),
            me.get("given_name"),
            me.get("family_name"),
            me.get("email"),
        )


class OrcidSignIn(OAuthSignIn):
    def __init__(self):
        super(OrcidSignIn, self).__init__("orcid")
        self.service = OAuth2Service(
            name="orcid",
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url="https://sandbox.orcid.org/oauth/authorize",
            access_token_url="https://sandbox.orcid.org/oauth/token",
            base_url="https://api.sandbox.orcid.org/v3.0/",
        )

    def authorize(self):
        return redirect(
            self.service.get_authorize_url(
                scope="/read-member",
                response_type="code",
                redirect_uri=self.get_callback_url(),
            )
        )

    def callback(self):
        def decode_json(payload):
            return json.loads(payload.decode("utf-8"))

        if "code" not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            data={
                "code": request.args["code"],
                "grant_type": "authorization_code",
                "redirect_uri": self.get_callback_url(),
            },
            decoder=decode_json,
        )

        me = oauth_session.get("https://www.googleapis.com/oauth2/v2/userinfo").json()

        return (
            me.get("id"),
            me.get("given_name"),
            me.get("family_name"),
            me.get("email"),
        )
