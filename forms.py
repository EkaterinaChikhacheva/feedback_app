from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, Length, NumberRange, Optional

class UserForm(FlaskForm):
   
    username = StringField("Username", validators=[InputRequired()])
    email = StringField("Email", validators = [InputRequired(), Email()])
    first_name= StringField('First Name', validators = [InputRequired()])
    last_name= StringField('Last Name', validators = [InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

class LoginForm(FlaskForm):
    username = StringField(
        'Username',
        validators = [InputRequired(), Length(min=1, max = 20)]
    )
    password = PasswordField(
        "Password",
        validators = [InputRequired(), Length(min=6, max = 55)]
    )

class DeleteForm(FlaskForm):
    """Delete form -- this form is intentionally blank."""

class FeedbackForm(FlaskForm):
    """Add feedback form"""

    title = StringField(
        'Title',
        validators = [InputRequired(), Length(max = 100)]
    )
    content = StringField(
        "Content",
        validators = [InputRequired()]
    )