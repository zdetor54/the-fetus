from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    FloatField,
    IntegerField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Email, NumberRange, Optional


class PatientContactForm(FlaskForm):
    id = StringField("PatiendID:", validators=[DataRequired()])
    home_phone = StringField("Σταθερό Τηλ:")
    mobile_phone = StringField("Κινητό Τηλ:")
    alternative_phone = StringField("Εναλλακτικό Τηλ:")
    email = StringField("Ε-mail:", validators=[Email()])


class BasicPatientForm(FlaskForm):
    id = StringField("PatiendID:", validators=[DataRequired()])
    first_name = StringField("Όνομα:", validators=[DataRequired()])
    last_name = StringField("Επώνυμο:", validators=[DataRequired()])
    father_name = StringField("Πατρώνυμο:")
    home_phone = StringField("Σταθερό Τηλ:")
    email = StringField("Ε-mail:", validators=[Email()])


class HistoryMedicalForm(FlaskForm):
    # System Fields
    id = IntegerField("Patient ID", validators=[Optional()])

    # Physical Measurements
    weight = FloatField(
        "Βάρος(kg):", validators=[Optional(), NumberRange(min=30, max=200)]
    )
    height = FloatField(
        "Ύψος(m):", validators=[Optional(), NumberRange(min=1, max=2.2)]
    )
    bmi = FloatField("BMI:", validators=[Optional()])

    # Habits
    smoking_before = StringField("Πριν:", validators=[Optional()])
    smoking_during = StringField("Κατά τη διάρκεια:", validators=[Optional()])
    alcohol = StringField("Αλκοόλ:", validators=[Optional()])

    # Medical History
    surgeries = TextAreaField(
        "Χειρουργεία:",
        validators=[Optional()],
        render_kw={"class": "expanding-textarea"},
    )
    transfusions_yn = BooleanField("Μεταγγίσεις:", validators=[Optional()])
    transfusions_reactions = StringField(
        "Αντιδράσεις σε μεταγγίσεις:", validators=[Optional()]
    )

    # Allergies
    allergies_yn = BooleanField("Σε φάρμακα:", validators=[Optional()])
    allergies_to_med = StringField("Σε φάρμακα:", validators=[Optional()])
    allergies_other = StringField("Άλλες:", validators=[Optional()])

    # Family History
    family_history = StringField("Οικογενειακό ιστορικό:", validators=[Optional()])

    # Medical Conditions
    heart_disease = StringField("Καρδιοπάθεια:", validators=[Optional()])
    hypertension = StringField("Υπέρταση:", validators=[Optional()])
    diabetes = StringField("Σακχαρώδης Διαβήτης:", validators=[Optional()])
    nephropathy = StringField("Νεφροπάθεια:", validators=[Optional()])
    liver_disease = StringField("Ηπατοπάθεια:", validators=[Optional()])
    thyroeidopatheia = StringField("Θυρεοειδοπάθεια:", validators=[Optional()])
    other_diseases = TextAreaField(
        "Άλλες Ασθένειες:",
        validators=[Optional()],
        render_kw={"class": "expanding-textarea"},
    )

    # Medications
    medication = StringField("Λήψη Φαρμάκων:", validators=[Optional()])

    # Gynecological History
    er_start = StringField("Έμμηνος Ρύση:", validators=[Optional()])
    er_nominator = StringField("ΕΡ αριθμητής:", validators=[Optional()])
    er_denominator = StringField("ΕΡ παρονομαστής:", validators=[Optional()])
    gynecological_surg = StringField(
        "Γυναικολογικές επεμβάσεις:", validators=[Optional()]
    )
    test_pap = StringField("Test Παπανικολάου:", validators=[Optional()])
    da = StringField("Διαγνωστικές Αποξέσεις:", validators=[Optional()])
    calt_vag_fluid = StringField("Καλλιέργεια κολπικού υγρού:", validators=[Optional()])

    # General Comments
    comments = TextAreaField(
        "Σχόλια:", validators=[Optional()], render_kw={"class": "expanding-textarea"}
    )

    submit = SubmitField("Αποθήκευση", validators=[Optional()])


class HistoryObstetricsForm(FlaskForm):
    id = IntegerField("Patient ID", validators=[Optional()])
    ft = IntegerField("Φυσιολογικοί Τοκετοί:", validators=[Optional()])
    kt = IntegerField("Τοκετοί με Καισαρική Τομή:", validators=[Optional()])
    embrioulkia = IntegerField("Εμβρυουλκία:", validators=[Optional()])
    te = IntegerField("Τεχνητές Εκτρώσεις:", validators=[Optional()])
    ae = IntegerField("Αυτόματες Εκτρώσεις:", validators=[Optional()])
    submit = SubmitField("Αποθήκευση", validators=[Optional()])
