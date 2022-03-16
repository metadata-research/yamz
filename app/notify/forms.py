from flask_wtf import FlaskForm
from wtforms import (
    TextAreaField,
    SubmitField,
)
from wtforms.validators import DataRequired, Length


class MessageForm(FlaskForm):
    message = TextAreaField(
        "Message", validators=[DataRequired(), Length(min=0, max=280)]
    )
    submit = SubmitField("Send")
