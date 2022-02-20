from flask import render_template, request, flash
from flask_login import current_user, login_required
from app.user import user_blueprint as user
from app.user.forms import EditProfileForm


@user.route("/")
def index():
    return render_template("user/index.jinja")


@user.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.last_name = form.last_name.data
        current_user.first_name = form.first_name.data
        current_user.email = form.email.data
        current_user.orcid = form.orcid.data
        current_user.enotify = form.enotify.data
        if current_user.is_administrator:
            current_user.reputation = form.reputation.data
        current_user.save()
        flash("Your changes have been saved.")
        return render_template("user/edit_profile.jinja", form=form)
    if request.method == "GET":
        form.last_name.data = current_user.last_name
        form.first_name.data = current_user.first_name
        form.email.data = current_user.email
        form.enotify.data = current_user.enotify
        if current_user.is_administrator:
            form.reputation.data = current_user.reputation
    return render_template("user/edit_profile.jinja", form=form)
