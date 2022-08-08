from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed

from wtforms import SubmitField


class DataFileUploadForm(FlaskForm):
    data_file = FileField(
        "data_file",
        validators=[FileRequired(), FileAllowed(["csv"], "csv files only.")],
    )
    submit = SubmitField("Upload")


class EmptyForm(FlaskForm):
    submit = SubmitField("Submit")
