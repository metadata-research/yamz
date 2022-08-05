from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed

from wtforms import SubmitField
from wtforms import validators


class FileUploadForm(FlaskForm):
    document_file = FileField(
        "document", validators=[FileRequired(), FileAllowed(["csv"], "csv files only.")]
    )
    submit = SubmitField("Upload")
