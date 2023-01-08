from flask import render_template

from app.ark import ark_blueprint as ark

@ark.route("/")
def index():
    return ('test', 200, {'Content-Type': 'text/plain; charset=utf-8'})