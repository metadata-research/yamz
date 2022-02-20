from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    EmailField,
    BooleanField,
    IntegerField,
)
from wtforms.validators import DataRequired, Email


class EditProfileForm(FlaskForm):
    last_name = StringField("Last Name", validators=[DataRequired()])
    first_name = StringField("First Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    enotify = BooleanField("Receive email notifications")
    reputation = IntegerField("Reputation")
    submit = SubmitField("Apply changes")
