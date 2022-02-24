from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired


class EmptyForm(FlaskForm):
    submit = SubmitField("Submit")


class CreateTermForm(FlaskForm):
    term_string = StringField("Term string", validators=[DataRequired()])
    definition = TextAreaField("Definition")
    examples = TextAreaField("Examples")
    submit = SubmitField("Submit")
