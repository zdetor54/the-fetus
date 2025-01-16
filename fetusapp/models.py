from fetusapp import db,login_manager
from flask import flash
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from datetime import datetime




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    last_updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    # Relationships
    created_patients = db.relationship('Patient', foreign_keys='Patient.created_by', backref='creator', lazy=True)
    updated_patients = db.relationship('Patient', foreign_keys='Patient.last_updated_by', backref='updater', lazy=True)


    def __init__(self, username, password, first_name, last_name, is_admin=False):
        self.username = username
        self.password_hash = generate_password_hash(password)
        if first_name is not None: 
            self.first_name = first_name
        if last_name is not None:
            self.last_name = last_name
        self.is_admin = is_admin

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"Username: {self.username}"

class Patient(db.Model, UserMixin):

    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    last_updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    last_updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    father_name = db.Column(db.String(64), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    marital_status = db.Column(db.String(32), nullable=True)
    nationality = db.Column(db.String(64), nullable=True)
    occupation = db.Column(db.String(64), nullable=True)
    street_name = db.Column(db.String(64), nullable=True)
    street_number = db.Column(db.String(16), nullable=True)
    city = db.Column(db.String(64), nullable=True)
    postal_code = db.Column(db.String(16), nullable=True)
    county = db.Column(db.String(64), nullable=True)
    home_phone = db.Column(db.String(16))
    mobile_phone = db.Column(db.String(16))
    alternative_phone = db.Column(db.String(16))
    email = db.Column(db.String(128))
    insurance = db.Column(db.String(64))
    insurance_comment = db.Column(db.String(128), nullable=True)
    amka = db.Column(db.String(16))
    spouse_name = db.Column(db.String(64))
    spouse_date_of_birth = db.Column(db.Date)
    spouse_occupation = db.Column(db.String(64))
    is_active = db.Column(db.Boolean, default=True)

    def __init__(self, first_name, last_name, father_name, date_of_birth, marital_status, nationality, occupation,
                 street_name, street_number, city, postal_code, county, home_phone=None, mobile_phone=None, alternative_phone=None,
                 email=None, insurance=None, insurance_comment=None, amka = None, spouse_name=None, spouse_date_of_birth=None, spouse_occupation=None,
                 created_by=None, last_updated_by=None):
        self.first_name = first_name
        self.last_name = last_name
        self.father_name = father_name
        self.date_of_birth = date_of_birth
        self.marital_status = marital_status
        self.nationality = nationality
        self.occupation = occupation
        self.street_name = street_name
        self.street_number = street_number
        self.city = city
        self.postal_code = postal_code
        self.county = county
        self.home_phone = home_phone
        self.mobile_phone = mobile_phone
        self.alternative_phone = alternative_phone
        self.email = email
        self.insurance = insurance
        self.insurance_comment = insurance_comment
        self.amka = amka
        self.spouse_name = spouse_name
        self.spouse_date_of_birth = spouse_date_of_birth
        self.spouse_occupation = spouse_occupation
        self.created_by = created_by
        self.last_updated_by = last_updated_by

    def __repr__(self):
        return f"Patient [{self.id}]: {self.first_name} {self.last_name} dob: {self.date_of_birth}"


# class Appointment(db.Model, UserMixin):
#     pass