from flask import render_template, redirect, url_for, flash, current_app
from flask_login import current_user, login_user, logout_user
from app import db
from app.user.models import User
from app.auth import auth_blueprint as auth
from app.auth.oauth import OAuthSignIn

@auth.route("/login/<portal_tag>")
@auth.route("/login")
def login(portal_tag=''):
    if current_user.is_authenticated:
        if portal_tag:
            return redirect(url_for("main.portal_index", portal_tag=portal_tag))
        else:
            return redirect(url_for("main.index"))
    return render_template("auth/login.jinja", portal_tag=portal_tag)

@auth.route("/logout/<portal_tag>")
@auth.route("/logout")
def logout(portal_tag=''):
    logout_user()
    if portal_tag:
        return redirect(url_for("main.portal_index", portal_tag=portal_tag))
    else:
        return redirect(url_for("main.index"))


@auth.route("/authorize/<provider>/<portal_tag>")
@auth.route("/authorize/<provider>")
def oauth_authorize(provider, portal_tag=''):

    if not current_user.is_anonymous:
        if portal_tag:
            return redirect(url_for("main.portal_index", portal_tag=portal_tag))
        else:
            return redirect(url_for("main.index"))

    oauth = OAuthSignIn.get_provider(provider)
    if portal_tag:
        return oauth.authorize(portal_tag=portal_tag)
    else:
        return oauth.authorize()

@auth.route("/<provider>" + "_authorized/<portal_tag>")
@auth.route("/<provider>" + "_authorized")
def oauth_callback(provider, portal_tag=''):
    if not current_user.is_anonymous:
        if portal_tag:
            return redirect(url_for("main.portal_index", portal_tag=portal_tag))
        else:
            return redirect(url_for("main.index"))

    oauth = OAuthSignIn.get_provider(provider)

    auth_id, first_name, last_name, email, orcid = oauth.callback()

    if auth_id is None:
        flash("Authentication failed.")
        if portal_tag:
            return redirect(url_for("main.portal_index", portal_tag=portal_tag))
        else:
            return redirect(url_for("main.index"))
    user = User.query.filter_by(auth_id=auth_id).first()

    if not user:
        # next_id = db.session.query(db.func.max(User.id)).scalar() + 1
        user = User(
            # id=next_id,
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
        if portal_tag:
            return redirect(url_for("main.portal_index", portal_tag=portal_tag))
        else:
            return redirect(url_for("main.index"))
