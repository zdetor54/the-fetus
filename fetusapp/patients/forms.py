from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from fetusapp.models import User


class PatientContactForm(FlaskForm):
    id = StringField('PatiendID:', validators=[DataRequired()])
    home_phone = StringField('Σταθερό Τηλ:')
    mobile_phone = StringField('Κινητό Τηλ:')
    alternative_phone = StringField('Εναλλακτικό Τηλ:')
    email = StringField('Ε-mail:', validators=[Email()])