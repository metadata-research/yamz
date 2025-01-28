import json

import orcid

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
        return url_for("auth.oauth_callback", provider=self.provider_name, _external=True)

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
        person = oauth_session.get(
            "https://www.googleapis.com/oauth2/v2/userinfo"
        ).json()

        return (
            person.get("id"),
            person.get("given_name"),
            person.get("family_name"),
            person.get("email"),
            None,
        )


class OrcidSignIn(OAuthSignIn):
    def __init__(self):
        super(OrcidSignIn, self).__init__("orcid")
        self.service = OAuth2Service(
            name="orcid",
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url=current_app.config["OAUTH_URLS"]["orcid"]["authorize_url"],
            access_token_url=current_app.config["OAUTH_URLS"]["orcid"][
                "access_token_url"
            ],
            base_url=current_app.config["OAUTH_URLS"]["orcid"]["base_url"],
        )

    def authorize(self):
        return redirect(
            self.service.get_authorize_url(
                scope="/read-limited",
                response_type="code",
                redirect_uri=self.get_callback_url(),
            )
        )

    # get_raw_access_token
    def callback(self):
        def decode_json(payload):
            return json.loads(payload.decode("utf-8"))

        if "code" not in request.args:
            return None, None, None
        raw_token = self.service.get_raw_access_token(
            data={
                "code": request.args["code"],
                "grant_type": "authorization_code",
                "redirect_uri": self.get_callback_url(),
            },
        )

        raw_token_json = raw_token.json()

        orc_id = raw_token_json["orcid"]
        token = raw_token_json["access_token"]

        api = orcid.MemberAPI(
            self.consumer_id,
            self.consumer_secret,
            sandbox=current_app.config["SANDBOX"],
        )

        person = api.read_record_member(
            orc_id, "person", token, put_code=None, accept_type="application/orcid+json"
        )

        return (
            orc_id,
            person["name"]["given-names"]["value"],
            person["name"]["family-name"]["value"],
            person["emails"]["email"][0]["email"]
            if len(person["emails"]["email"]) > 0
            else "",
            orc_id,
        )
