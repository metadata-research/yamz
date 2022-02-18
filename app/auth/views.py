from flask import render_template, redirect, url_for, current_app
from flask_login import current_user
from app.auth import auth_blueprint as auth
from app.auth.oauth import OAuthSignIn


@auth.route("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    return render_template("auth/login.jinja")


@auth.route("/logout")
def logout():
    return redirect(url_for("auth.login"))


@auth.route("/authorize/<provider>")
def oauth_authorize(provider):
    if not current_user.is_anonymous():
        return redirect(url_for("index"))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()
