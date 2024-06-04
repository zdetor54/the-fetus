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

class BasicPatientForm(FlaskForm):
    id = StringField('PatiendID:', validators=[DataRequired()])
    first_name = StringField('Όνομα:', validators=[DataRequired()])
    last_name = StringField('Επώνυμο:', validators=[DataRequired()])
    father_name = StringField('Πατρώνυμο:')
    home_phone = StringField('Σταθερό Τηλ:')
    email = StringField('Ε-mail:', validators=[Email()])