from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class DataFileUploadForm(FlaskForm):
    name = StringField("Name Import", validators=[DataRequired()])
    description = TextAreaField("Describe Import")
    data_file = FileField(
        "data_file",
        validators=[FileRequired(), FileAllowed(["csv"], "csv files only.")],
    )
    submit = SubmitField("Upload")


class EmptyForm(FlaskForm):
    submit = SubmitField("Submit")
