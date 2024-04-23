from fetusapp import db,login_manager
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from datetime import datetime




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    usename = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    last_updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    patients = db.relationship('Patient', backref='user', lazy=True)

    def __init__(self, username, password, first_name, last_name):
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"Username: {self.username}"

class Patient(db.Model, UserMixin):

    __tablename__ = 'patients'
    
    users = db.relationship(User)

    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    last_updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    last_updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    dob = db.Column(db.DateTime)

    def __init__(self, first_name, last_name, dob):
        self.first_name = first_name
        self.last_name = last_name
        self.dob = dob

    def __repr__(self):
        return f"Patient: {self.first_name} {self.last_name}"


# class Appointment(db.Model, UserMixin):
#     pass