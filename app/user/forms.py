from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    DataRequired,
    SubmitField,
)


class UserInfoForm(FlaskForm):
    last_name = StringField("Last Name", validators=[DataRequired()])
    first_name = StringField("First Name", validators=[DataRequired()])
    orcid = StringField("ORCiD")
    submit = SubmitField("Submit")
