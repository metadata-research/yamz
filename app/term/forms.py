from flask import request
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField, SelectField, BooleanField
from wtforms.validators import DataRequired
from flask_pagedown.fields import PageDownField


class CreateTermForm(FlaskForm):
    term_string = StringField("Term string", validators=[DataRequired()])
    definition = PageDownField("Definition")
    examples = PageDownField("Examples")
    draft =  BooleanField("Draft", default=True)
    submit = SubmitField("Submit")


class CommentForm(FlaskForm):
    comment_string = PageDownField("Comment", validators=[DataRequired()])
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
        if "portal_tag" in kwargs:
            self.portal_tag = kwargs.pop("portal_tag") 

        super(SearchForm, self).__init__(*args, **kwargs)


class TagForm(FlaskForm):
    category = StringField("Category", validators=[DataRequired()], default="community")
    value = StringField("Value", validators=[DataRequired()])
    description = TextAreaField("Description")
    submit = SubmitField("Save")


class AddTagForm(FlaskForm):
    tag_list = SelectField("Tag", choices=["a", "b", "c"])

    submit = SubmitField("Apply")
