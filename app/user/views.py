from flask import render_template, request
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
    if request.method == "GET":
        form.last_name.data = current_user.last_name
        form.first_name.data = current_user.first_name
        form.email.data = current_user.email

    return render_template("user/edit_profile.jinja", form=form)
