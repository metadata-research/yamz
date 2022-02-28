from flask import request
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired


class CreateTermForm(FlaskForm):
    term_string = StringField("Term string", validators=[DataRequired()])
    definition = TextAreaField("Definition")
    examples = TextAreaField("Examples")
    submit = SubmitField("Submit")


class CommentForm(FlaskForm):
    comment_string = TextAreaField("Comment", validators=[DataRequired()])
    submit = SubmitField("Comment")


class EmptyForm(FlaskForm):
    submit = SubmitField("Submit")


class SearchForm(FlaskForm):
    q = StringField("Search", validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if "formdata" not in kwargs:
            kwargs["formdata"] = request.args
        if "csrf_enabled" not in kwargs:
            kwargs["csrf_enabled"] = False
        super(SearchForm, self).__init__(*args, **kwargs)
