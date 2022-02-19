from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    EmailField,
    BooleanField,
)
from wtforms.validators import DataRequired, Email, Length, EqualTo


class EditProfileForm(FlaskForm):
    last_name = StringField("Last Name", validators=[DataRequired()])
    first_name = StringField("First Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    orcid = StringField("ORCiD")
    receive_notifications = BooleanField("Receive email notifications")
    submit = SubmitField("Apply changes")
