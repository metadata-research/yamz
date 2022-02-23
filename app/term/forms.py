from flask_wtf import FlaskForm
from wtforms import SubmitField


class EmptyForm(FlaskForm):
    submit = SubmitField("Submit")
