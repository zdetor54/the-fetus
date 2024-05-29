from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from fetusapp.models import User


class FindPatientForm(FlaskForm):
    # email = StringField('Email', validators=[DataRequired(), Email()])
    home_phone = StringField('Home Phone')
    mobile_phone = StringField('Mobile Phone')
    alternative_phone = StringField('Alternative Phone')
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    submit = SubmitField('Register')