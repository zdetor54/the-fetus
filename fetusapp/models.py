from datetime import datetime
from decimal import Decimal

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from fetusapp import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class BaseModel(db.Model):
    """Base model class with common functionality"""

    __abstract__ = True

    def to_dict(self):
        """Convert SQLAlchemy model to dictionary automatically."""
        dictionary = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)

            # Handle special data types
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, Decimal):
                value = float(value)

            dictionary[column.name] = value

        return dictionary


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    last_updated_on = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now()
    )

    # Relationships
    created_patients = db.relationship(
        "Patient", foreign_keys="Patient.created_by", backref="creator", lazy=True
    )
    updated_patients = db.relationship(
        "Patient", foreign_keys="Patient.last_updated_by", backref="updater", lazy=True
    )

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
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    last_updated_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    last_updated_on = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now()
    )

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

    def __init__(
        self,
        first_name,
        last_name,
        father_name=None,
        date_of_birth=None,
        marital_status=None,
        nationality=None,
        occupation=None,
        street_name=None,
        street_number=None,
        city=None,
        postal_code=None,
        county=None,
        home_phone=None,
        mobile_phone=None,
        alternative_phone=None,
        email=None,
        insurance=None,
        insurance_comment=None,
        amka=None,
        spouse_name=None,
        spouse_date_of_birth=None,
        spouse_occupation=None,
        created_by=None,
        last_updated_by=None,
    ):
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

    def deactivate(self, user_id):
        """Soft delete the patient by marking as inactive"""
        self.is_active = False
        self.last_updated_by = user_id
        self.last_updated_on = datetime.utcnow()
        db.session.commit()

    def __repr__(self):
        return f"Patient [{self.id}]: {self.first_name} {self.last_name} dob: {self.date_of_birth}"


class HistoryMedical(BaseModel):
    __tablename__ = "history_medical"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    last_updated_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    last_updated_on = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now()
    )

    # Medical History
    surgeries = db.Column(db.Text, nullable=True)
    smoking_before = db.Column(db.String(64), nullable=True)
    smoking_during = db.Column(db.String(64), nullable=True)
    alcohol = db.Column(db.Text, nullable=True)
    transfusions_yn = db.Column(db.Boolean, default=False)
    transfusions_reactions = db.Column(db.Text, nullable=True)
    allergies_yn = db.Column(db.Boolean, default=False)
    allergies_to_med = db.Column(db.Text, nullable=True)
    allergies_other = db.Column(db.Text, nullable=True)
    family_history = db.Column(db.Text, nullable=True)
    weight = db.Column(db.Numeric(5, 2), nullable=True)
    height = db.Column(db.Numeric(3, 2), nullable=True)
    bmi = db.Column(db.Numeric(5, 3), nullable=True)
    comments = db.Column(db.Text, nullable=True)

    # Pathologies
    heart_disease = db.Column(db.Text, nullable=True)
    hypertension = db.Column(db.Text, nullable=True)
    diabetes = db.Column(db.Text, nullable=True)
    nephropathy = db.Column(db.Text, nullable=True)
    liver_disease = db.Column(db.Text, nullable=True)
    thyroeidopatheia = db.Column(db.Text, nullable=True)
    other_diseases = db.Column(db.Text, nullable=True)
    medication = db.Column(db.Text, nullable=True)

    # Gynecological History
    er_start = db.Column(db.String(64), nullable=True)
    er_nominator = db.Column(db.String(64), nullable=True)
    er_denominator = db.Column(db.String(64), nullable=True)
    gynecological_surg = db.Column(db.Text, nullable=True)
    test_pap = db.Column(db.Text, nullable=True)
    da = db.Column(db.Text, nullable=True)
    calt_vag_fluid = db.Column(db.String(32), nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    patient = db.relationship(
        "Patient", backref=db.backref("medical_history", lazy=True)
    )
    creator = db.relationship(
        "User", foreign_keys=[created_by], backref="created_medical_histories"
    )
    updater = db.relationship(
        "User", foreign_keys=[last_updated_by], backref="updated_medical_histories"
    )

    def __init__(
        self,
        patient_id,
        created_by,
        last_updated_by,
        surgeries=None,
        smoking_before=None,
        smoking_during=None,
        alcohol=None,
        transfusions_yn=False,
        transfusions_reactions=None,
        allergies_yn=False,
        allergies_to_med=None,
        allergies_other=None,
        family_history=None,
        weight=None,
        height=None,
        bmi=None,
        comments=None,
        heart_disease=None,
        hypertension=None,
        diabetes=None,
        nephropathy=None,
        liver_disease=None,
        thyroeidopatheia=None,
        other_diseases=None,
        medication=None,
        er_start=None,
        er_nominator=None,
        er_denominator=None,
        gynecological_surg=None,
        test_pap=None,
        da=None,
        calt_vag_fluid=None,
    ):
        self.patient_id = patient_id
        self.created_by = created_by
        self.last_updated_by = last_updated_by

        # Medical History
        self.surgeries = surgeries
        self.smoking_before = smoking_before
        self.smoking_during = smoking_during
        self.alcohol = alcohol
        self.transfusions_yn = transfusions_yn
        self.transfusions_reactions = transfusions_reactions
        self.allergies_yn = allergies_yn
        self.allergies_to_med = allergies_to_med
        self.allergies_other = allergies_other
        self.family_history = family_history
        self.weight = weight
        self.height = height
        self.bmi = bmi
        self.comments = comments

        # Pathologies
        self.heart_disease = heart_disease
        self.hypertension = hypertension
        self.diabetes = diabetes
        self.nephropathy = nephropathy
        self.liver_disease = liver_disease
        self.thyroeidopatheia = thyroeidopatheia
        self.other_diseases = other_diseases
        self.medication = medication

        # Gynecological History
        self.er_start = er_start
        self.er_nominator = er_nominator
        self.er_denominator = er_denominator
        self.gynecological_surg = gynecological_surg
        self.test_pap = test_pap
        self.da = da
        self.calt_vag_fluid = calt_vag_fluid
