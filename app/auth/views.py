from flask import render_template, redirect, url_for, flash, current_app
from flask_login import current_user, login_user, logout_user
from app import db
from app.user.models import User
from app.auth import auth_blueprint as auth
from app.auth.oauth import OAuthSignIn


@auth.route("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    return render_template("auth/login.jinja")


@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))


@auth.route("/authorize/<provider>")
def oauth_authorize(provider):

    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))

    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@auth.route("/<provider>" + "_authorized")
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))
    oauth = OAuthSignIn.get_provider(provider)

    auth_id, given_name, family_name, email = oauth.callback()
    if auth_id is None:
        flash("Authentication failed.")
        return redirect(url_for("main.index"))
    user = User.query.filter_by(auth_id=auth_id).first()

    if not user:
        user = User(
            authority=provider,
            auth_id=auth_id,
            last_name=given_name,
            first_name=family_name,
            reputation="30",
            email=email,
        )
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        is_new_user = True

    login(user, True)
    if is_new_user:
        return redirect(url_for("user.edit_profile", new_user=is_new_user))
    else:
        return redirect(url_for("main.index"))
