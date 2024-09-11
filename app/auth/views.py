from flask import render_template, redirect, url_for, flash, session
from flask_login import current_user, login_user, logout_user
from app import db
from app.user.models import User
from app.auth import auth_blueprint as auth
from app.auth.oauth import OAuthSignIn

def redirect_authenticated_user():
    if session.get("portal_tag", None):
        return redirect(url_for("main.portal_index", portal_tag=session["portal_tag"]))
    return redirect(url_for("main.index"))


@auth.route("/login")
def login():
    if current_user.is_authenticated:
        return redirect_authenticated_user()
    return render_template("auth/login.jinja")


@auth.route("/logout")
def logout():
    logout_user()
    return redirect_authenticated_user()

@auth.route("/authorize/<provider>")
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect_authenticated_user()

    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@auth.route("/<provider>" + "_authorized")
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect_authenticated_user()

    oauth = OAuthSignIn.get_provider(provider)
    auth_id, first_name, last_name, email, orcid = oauth.callback()

    if auth_id is None:
        flash("Authentication failed.")
        return redirect_authenticated_user()

    user = User.query.filter_by(auth_id=auth_id).first()
    if not user:
        user = User(
            authority=provider,
            auth_id=auth_id,
            last_name=last_name,
            first_name=first_name,
            reputation="30",
            email=email,
            orcid=orcid,
        )
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        is_new_user = True
        login_user(user, True)
        return redirect(url_for("user.edit_profile", new_user=is_new_user))

    login_user(user, True)
    return redirect_authenticated_user()