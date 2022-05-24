from flask import request
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired
from flask_pagedown.fields import PageDownField


class CreateTermForm(FlaskForm):
    term_string = StringField("Term string", validators=[DataRequired()])
    definition = PageDownField("Definition")
    examples = PageDownField("Examples")
    submit = SubmitField("Submit")


class CommentForm(FlaskForm):
    comment_string = TextAreaField("Comment", validators=[DataRequired()])
    submit = SubmitField("Comment")


class EmptyForm(FlaskForm):
    submit = SubmitField("Submit")


class SearchForm(FlaskForm):
    q = StringField("Search for a term", validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if "formdata" not in kwargs:
            kwargs["formdata"] = request.args
        if "csrf_enabled" not in kwargs:
            kwargs["csrf_enabled"] = False
        super(SearchForm, self).__init__(*args, **kwargs)


class TagForm(FlaskForm):
    category = StringField("Category", validators=[DataRequired()], default="community")
    value = StringField("Value", validators=[DataRequired()])
    description = TextAreaField("Description")
    submit = SubmitField("Save")
