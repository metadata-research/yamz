from wtforms import StringField, TextAreaField, SelectField, SubmitField
from flask import request
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField, SelectField, BooleanField, HiddenField
from wtforms.validators import DataRequired
from flask_pagedown.fields import PageDownField
from app.term.models import Tag


class CreateTermForm(FlaskForm):
    term_string = StringField("Term string", validators=[DataRequired()])
    definition = PageDownField("Definition")
    examples = PageDownField("Examples")
    draft = BooleanField("Draft", default=True)
    submit = SubmitField("Submit")


class CommentForm(FlaskForm):
    comment_string = PageDownField("Comment", validators=[DataRequired()])
    submit = SubmitField("Comment")


class EmptyForm(FlaskForm):
    submit = SubmitField("")


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
    category = SelectField("Category", validators=[
                           DataRequired()], choices=[], default="community")
    value = StringField("Value", validators=[DataRequired()])
    domain = StringField("Domain")
    description = TextAreaField("Description")
    submit = SubmitField("Save")


class EditTagForm(FlaskForm):
    category = StringField("Category", validators=[
                           DataRequired()])
    value = StringField("Value", validators=[DataRequired()])
    domain = StringField("Domain")
    description = TextAreaField("Description")
    submit = SubmitField("Save")


class AddTagForm(FlaskForm):
    tag_list = SelectField("Tag", choices=[])
    submit = SubmitField("Apply Tag")


class AddRelationshipForm(FlaskForm):
    subject_id = StringField("Subject", validators=[DataRequired()])
    predicate_id = SelectField("Predicate", validators=[
        DataRequired()], choices=[])
    object_id = StringField("Object", validators=[DataRequired()])
    submit = SubmitField("Submit")


class EditRelationshipForm(FlaskForm):
    subject_term_string = StringField("Subject", validators=[DataRequired()])
    predicate_id = SelectField("Predicate", validators=[
                               DataRequired()], choices=[])
    object_term_string = StringField("Object", validators=[DataRequired()])
    submit = SubmitField("Save Changes")


class EditTermSetForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField("Description")
    # tag_list = SelectField("Tags", choices=[], coerce=int)
    source = StringField("Source")
    submit = SubmitField("Save")

    '''
    def __init__(self, *args, **kwargs):
        super(EditTermSetForm, self).__init__(*args, **kwargs)
        self.tag_list.choices = [(tag.id, tag.value)
                                 for tag in Tag.query.order_by(Tag.value).all()]
    '''


class AddSubClassForm(FlaskForm):
    parent_term_id = StringField("Parent Term ID", validators=[DataRequired()])
    child_id = StringField("Term ID", validators=[DataRequired()])
    submit = SubmitField("Add Subclass")
