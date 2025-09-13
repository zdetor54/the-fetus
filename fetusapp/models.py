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


class User(BaseModel, UserMixin):
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


class Patient(BaseModel):
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


class HistoryObstetrics(BaseModel):
    __tablename__ = "history_obstetrics"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    last_updated_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    last_updated_on = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now()
    )

    # Obstetric History fields (example, adjust as per your JSON)
    ft = db.Column(db.Integer, nullable=True)  # Full-term births
    kt = db.Column(db.Integer, nullable=True)  # Premature births
    embrioulkia = db.Column(db.Integer, nullable=True)  # Miscarriages
    te = db.Column(db.Integer, nullable=True)  # Ectopic pregnancies
    ae = db.Column(db.Integer, nullable=True)  # Stillbirths
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    patient = db.relationship(
        "Patient", backref=db.backref("obstetric_history", lazy=True)
    )
    creator = db.relationship(
        "User", foreign_keys=[created_by], backref="created_obstetric_histories"
    )
    updater = db.relationship(
        "User",
        foreign_keys=[last_updated_by],
        backref="updated_obstetric_histories",
    )

    def __init__(
        self,
        patient_id,
        created_by,
        last_updated_by,
        ft=None,
        kt=None,
        embrioulkia=None,
        te=None,
        ae=None,
        is_active=True,
    ):
        self.patient_id = patient_id
        self.created_by = created_by
        self.last_updated_by = last_updated_by
        self.ft = ft
        self.kt = kt
        self.embrioulkia = embrioulkia
        self.te = te
        self.ae = ae
        self.is_active = is_active


class HistoryObstetrics_x(BaseModel):
    __tablename__ = "history_obstetrics_x"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    last_updated_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    last_updated_on = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now()
    )

    year_of_birth = db.Column(db.Integer, nullable=True)
    birth_type = db.Column(db.String(50), nullable=True)
    baby_weight = db.Column(db.Numeric(5, 2), nullable=True)
    gestation_week = db.Column(db.Integer, nullable=True)
    complications_notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    patient = db.relationship(
        "Patient", backref=db.backref("obstetric_history_x", lazy=True)
    )
    creator = db.relationship(
        "User", foreign_keys=[created_by], backref="created_obstetric_histories_x"
    )
    updater = db.relationship(
        "User",
        foreign_keys=[last_updated_by],
        backref="updated_obstetric_histories_x",
    )

    def __init__(
        self,
        patient_id,
        created_by,
        last_updated_by,
        year_of_birth=None,
        birth_type=None,
        baby_weight=None,
        gestation_week=None,
        complications_notes=None,
        is_active=True,
    ):
        self.patient_id = patient_id
        self.created_by = created_by
        self.last_updated_by = last_updated_by
        self.year_of_birth = year_of_birth
        self.birth_type = birth_type
        self.baby_weight = baby_weight
        self.gestation_week = gestation_week
        self.complications_notes = complications_notes
        self.is_active = is_active


class PregnancyHistory(BaseModel):
    __tablename__ = "pregnancy_history"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    last_updated_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    last_updated_on = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now()
    )

    # Pregnancy-level fields (from tblpregnancyhistory)
    ter = db.Column(db.Date, nullable=False)
    alcohol = db.Column(db.String(128), nullable=True)
    smoking = db.Column(db.String(128), nullable=True)
    amniocentesis = db.Column(db.String(128), nullable=True)
    medication = db.Column(db.String(128), nullable=True)
    other = db.Column(db.String(128), nullable=True)
    diabetes = db.Column(db.String(128), nullable=True)
    hypertension = db.Column(db.String(128), nullable=True)
    urine_albumin = db.Column(db.String(128), nullable=True)
    bleeding = db.Column(db.String(128), nullable=True)
    blood_type = db.Column(db.String(64), nullable=True)
    rhesus = db.Column(db.String(32), nullable=True)
    hemoglobinopathies_bth = db.Column(db.String(128), nullable=True)
    hemoglobinopathies_bs = db.Column(db.String(128), nullable=True)
    vaginal_fluid_cultivation = db.Column(db.String(128), nullable=True)
    mycoplasma_ureaplasma = db.Column(db.String(128), nullable=True)
    chlamydia = db.Column(db.String(128), nullable=True)
    herpes_hsv = db.Column(db.String(128), nullable=True)
    hiv_12 = db.Column(db.String(128), nullable=True)
    syphilis_vdlr = db.Column(db.String(128), nullable=True)
    hepatitis_b_bhsag = db.Column(db.String(128), nullable=True)
    aids_hiv = db.Column(db.String(128), nullable=True)
    red_cells = db.Column(db.String(128), nullable=True)
    toxoplasma = db.Column(db.String(128), nullable=True)
    cytomegalovirus_cmv = db.Column(db.String(128), nullable=True)
    listeria = db.Column(db.String(128), nullable=True)
    hcv = db.Column(db.String(128), nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    patient = db.relationship("Patient", backref=db.backref("pregnancies", lazy=True))
    creator = db.relationship(
        "User", foreign_keys=[created_by], backref="created_pregnancies"
    )
    updater = db.relationship(
        "User", foreign_keys=[last_updated_by], backref="updated_pregnancies"
    )

    def __init__(
        self,
        patient_id,
        created_by,
        last_updated_by,
        ter=None,
        alcohol=None,
        smoking=None,
        amniocentesis=None,
        medication=None,
        other=None,
        diabetes=None,
        hypertension=None,
        urine_albumin=None,
        bleeding=None,
        blood_type=None,
        rhesus=None,
        hemoglobinopathies_bth=None,
        hemoglobinopathies_bs=None,
        vaginal_fluid_cultivation=None,
        mycoplasma_ureaplasma=None,
        chlamydia=None,
        herpes_hsv=None,
        hiv_12=None,
        syphilis_vdlr=None,
        hepatitis_b_bhsag=None,
        aids_hiv=None,
        red_cells=None,
        toxoplasma=None,
        cytomegalovirus_cmv=None,
        listeria=None,
        hcv=None,
        is_active=True,
    ):
        self.patient_id = patient_id
        self.created_by = created_by
        self.last_updated_by = last_updated_by
        self.ter = ter
        self.alcohol = alcohol
        self.smoking = smoking
        self.amniocentesis = amniocentesis
        self.medication = medication
        self.other = other
        self.diabetes = diabetes
        self.hypertension = hypertension
        self.urine_albumin = urine_albumin
        self.bleeding = bleeding
        self.blood_type = blood_type
        self.rhesus = rhesus
        self.hemoglobinopathies_bth = hemoglobinopathies_bth
        self.hemoglobinopathies_bs = hemoglobinopathies_bs
        self.vaginal_fluid_cultivation = vaginal_fluid_cultivation
        self.mycoplasma_ureaplasma = mycoplasma_ureaplasma
        self.chlamydia = chlamydia
        self.herpes_hsv = herpes_hsv
        self.hiv_12 = hiv_12
        self.syphilis_vdlr = syphilis_vdlr
        self.hepatitis_b_bhsag = hepatitis_b_bhsag
        self.aids_hiv = aids_hiv
        self.red_cells = red_cells
        self.toxoplasma = toxoplasma
        self.cytomegalovirus_cmv = cytomegalovirus_cmv
        self.listeria = listeria
        self.hcv = hcv
        self.is_active = is_active


class PregnancyHistory_x(BaseModel):
    __tablename__ = "pregnancy_history_x"

    id = db.Column(db.Integer, primary_key=True)
    pregnancy_id = db.Column(
        db.Integer, db.ForeignKey("pregnancy_history.id"), nullable=False
    )
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    last_updated_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    last_updated_on = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now()
    )

    # Visit-level fields (from tblpregnancyhistory_x)
    date_of_visit = db.Column(db.Date, nullable=True)
    cause_of_visit = db.Column(db.String(128), nullable=True)
    tokos = db.Column(db.Integer, nullable=True)
    pregnancy_age = db.Column(db.String(64), nullable=True)
    height = db.Column(db.Numeric(5, 2), nullable=True)
    weight_begin = db.Column(db.Numeric(5, 2), nullable=True)
    weight_current = db.Column(db.Numeric(5, 2), nullable=True)
    weight_change = db.Column(db.Numeric(5, 2), nullable=True)
    presentation = db.Column(db.String(64), nullable=True)
    fetal_heart = db.Column(db.String(64), nullable=True)
    amniotic_sac = db.Column(db.String(64), nullable=True)
    contractions = db.Column(db.String(64), nullable=True)
    cervical_dilation = db.Column(db.String(64), nullable=True)
    cervical_effacement = db.Column(db.String(64), nullable=True)
    arterial_pressure = db.Column(db.String(64), nullable=True)
    temperature = db.Column(db.Numeric(5, 2), nullable=True)
    sumphysial_fundal_height_sfh = db.Column(db.Numeric(6, 2), nullable=True)
    comments = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    pregnancy = db.relationship(
        "PregnancyHistory", backref=db.backref("visits", lazy=True)
    )
    creator = db.relationship(
        "User", foreign_keys=[created_by], backref="created_pregnancy_visits"
    )
    updater = db.relationship(
        "User", foreign_keys=[last_updated_by], backref="updated_pregnancy_visits"
    )

    def __init__(
        self,
        pregnancy_id,
        created_by,
        last_updated_by,
        date_of_visit=None,
        cause_of_visit=None,
        tokos=None,
        pregnancy_age=None,
        height=None,
        weight_begin=None,
        weight_current=None,
        weight_change=None,
        presentation=None,
        fetal_heart=None,
        amniotic_sac=None,
        contractions=None,
        cervical_dilation=None,
        cervical_effacement=None,
        arterial_pressure=None,
        temperature=None,
        sumphysial_fundal_height_sfh=None,
        comments=None,
        is_active=True,
    ):
        self.pregnancy_id = pregnancy_id
        self.created_by = created_by
        self.last_updated_by = last_updated_by
        self.date_of_visit = date_of_visit
        self.cause_of_visit = cause_of_visit
        self.tokos = tokos
        self.pregnancy_age = pregnancy_age
        self.height = height
        self.weight_begin = weight_begin
        self.weight_current = weight_current
        self.weight_change = weight_change
        self.presentation = presentation
        self.fetal_heart = fetal_heart
        self.amniotic_sac = amniotic_sac
        self.contractions = contractions
        self.cervical_dilation = cervical_dilation
        self.cervical_effacement = cervical_effacement
        self.arterial_pressure = arterial_pressure
        self.temperature = temperature
        self.sumphysial_fundal_height_sfh = sumphysial_fundal_height_sfh
        self.comments = comments
        self.is_active = is_active
