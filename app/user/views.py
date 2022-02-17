from flask import render_template
from app.user import user_blueprint as user


@user.route("/")
def index():
    return render_template("user/index.jinja")
