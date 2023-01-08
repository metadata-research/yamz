from flask import render_template

from app.ark import ark_blueprint as ark

@ark.route("/")
def index():
    return render_template("ark/index.jinja")