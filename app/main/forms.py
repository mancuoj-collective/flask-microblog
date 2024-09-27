import sqlalchemy as sa
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError

from app import db
from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    about_me = TextAreaField(
        "About me",
        validators=[Length(min=0, max=140)],
        render_kw={"rows": 3, "maxlength": 140},
    )
    submit = SubmitField("Submit")

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(
                sa.select(User).where(User.username == username.data)
            )
            if user is not None:
                raise ValidationError("Please use a different username.")


class EmptyForm(FlaskForm):
    submit = SubmitField("Submit")


class PostForm(FlaskForm):
    post = TextAreaField(
        "",
        validators=[DataRequired(), Length(min=1, max=140)],
        render_kw={"placeholder": "Say something ...", "rows": 3, "maxlength": 140},
    )
    submit = SubmitField("Submit")
