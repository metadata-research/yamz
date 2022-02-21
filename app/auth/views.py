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

    auth_id, first_name, last_name, email, orcid = oauth.callback()

    if auth_id is None:
        flash("Authentication failed.")
        return redirect(url_for("main.index"))
    user = User.query.filter_by(auth_id=auth_id).first()

    if not user:
        # TODO: lock the table db.session.query(User).with_for_update()
        next_id = db.session.query(db.func.max(User.id)).scalar() + 1
        user = User(
            id=next_id,
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

    else:
        login_user(user, True)
        return redirect(url_for("main.index"))
