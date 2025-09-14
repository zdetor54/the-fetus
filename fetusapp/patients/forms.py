from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    FieldList,
    FloatField,
    FormField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.fields import DateField
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
    kt = IntegerField("Καισαρικές:", validators=[Optional()])
    embrioulkia = IntegerField("Εμβρυουλκία:", validators=[Optional()])
    te = IntegerField("Τεχνητές Εκτρώσεις:", validators=[Optional()])
    ae = IntegerField("Αυτόματες Εκτρώσεις:", validators=[Optional()])


class HistoryObstetricsXEntryForm(FlaskForm):
    id = IntegerField("ID", validators=[Optional()])
    year_of_birth = IntegerField("Έτος Γέννησης:", validators=[Optional()])
    birth_type = SelectField(
        "Τύπος Τοκετού:",
        validators=[Optional()],
        choices=[
            ("Φυσιολογικός Τοκετός", "Φυσιολογικός Τοκετός"),
            ("Καισαρική Τομή", "Καισαρική Τομή"),
            ("Εμβρυουλκία", "Εμβρυουλκία"),
        ],
    )
    baby_weight = FloatField("Βάρος Νεογνού (kg):", validators=[Optional()])
    gestation_week = IntegerField("Εβδομάδα Κύησης:", validators=[Optional()])
    complications_notes = TextAreaField(
        "Επιπλοκές / Παρατηρήσεις:",
        validators=[Optional()],
        render_kw={"class": "expanding-textarea"},
    )


class HistoryObstetricsXForm(FlaskForm):
    entries = FieldList(FormField(HistoryObstetricsXEntryForm), min_entries=0)


# ---------------- Pregnancy History (master) & Visits (detail) ---------------- #


class PregnancyHistoryEntryForm(FlaskForm):
    """Top-level pregnancy record (one per pregnancy)"""

    id = IntegerField("ID", validators=[Optional()])
    ter = DateField("Τελευταία Έμμηνος Ρύση:", validators=[Optional()])
    alcohol = StringField("Αλκοόλ:", validators=[Optional()])
    smoking = StringField("Κάπνισμα:", validators=[Optional()])
    amniocentesis = StringField("Αμνιοκέντηση:", validators=[Optional()])
    medication = StringField("Φαρμακευτική Αγωγή:", validators=[Optional()])
    other = StringField("Λοιπά:", validators=[Optional()])
    diabetes = StringField("Σακχαρώδης Διαβήτης:", validators=[Optional()])
    hypertension = StringField("Υπέρταση:", validators=[Optional()])
    urine_albumin = StringField("Λεύκωμα Ούρων:", validators=[Optional()])
    bleeding = StringField("Αιμορραγία:", validators=[Optional()])
    blood_type = StringField("Ομάδα Αίματος:", validators=[Optional()])
    rhesus = StringField("Rhesus:", validators=[Optional()])
    hemoglobinopathies_bth = StringField(
        "Αιμοσφαιρινοπάθειες βth:", validators=[Optional()]
    )
    hemoglobinopathies_bs = StringField(
        "Αιμοσφαιρινοπάθειες βs:", validators=[Optional()]
    )
    vaginal_fluid_cultivation = StringField(
        "Καλλιέργεια Κολπικού Υγρού:", validators=[Optional()]
    )
    mycoplasma_ureaplasma = StringField(
        "Μυκόπλασμα/Ουρεόπλασμα:", validators=[Optional()]
    )
    chlamydia = StringField("Χλαμύδια:", validators=[Optional()])
    herpes_hsv = StringField("Έρπητας (HSV):", validators=[Optional()])
    hiv_12 = StringField("HIV 1-2:", validators=[Optional()])
    syphilis_vdlr = StringField("Σύφιλη - VDRL:", validators=[Optional()])
    hepatitis_b_bhsag = StringField("Ηπατίτιδα B-ΗΒsAg:", validators=[Optional()])
    aids_hiv = StringField("AIDS/HIV:", validators=[Optional()])
    red_cells = StringField("Ερυθρά Αιμοσφαίρια:", validators=[Optional()])
    toxoplasma = StringField("Τοξόπλασμα:", validators=[Optional()])
    cytomegalovirus_cmv = StringField(
        "Κυτταρομεγαλοϊός - CMV:", validators=[Optional()]
    )
    listeria = StringField("Λιστέρια:", validators=[Optional()])
    hcv = StringField("HCV:", validators=[Optional()])


class PregnancyHistoryForm(FlaskForm):
    """Container for multiple pregnancy history entries"""

    entries = FieldList(FormField(PregnancyHistoryEntryForm), min_entries=0)


class PregnancyHistoryXEntryForm(FlaskForm):
    """Single antenatal visit (PregnancyHistory_x)"""

    id = IntegerField("ID", validators=[Optional()])
    date_of_visit = DateField("Ημ/νία Επίσκεψης:", validators=[Optional()])
    cause_of_visit = StringField("Αιτία Επίσκεψης:", validators=[Optional()])
    tokos = IntegerField("Τοκός:", validators=[Optional()])
    pregnancy_age = StringField("Ηλικία Κύησης:", validators=[Optional()])
    height = FloatField("Ύψος (cm):", validators=[Optional()])
    weight_begin = FloatField("Βάρος Έναρξης (kg):", validators=[Optional()])
    weight_current = FloatField("Τρέχον Βάρος (kg):", validators=[Optional()])
    weight_change = FloatField("Μεταβολή Βάρους (kg):", validators=[Optional()])
    presentation = StringField("Θέση Εμβρύου:", validators=[Optional()])
    fetal_heart = StringField("Καρδιακοί Παλμοί Εμβρύου:", validators=[Optional()])
    amniotic_sac = StringField("Αμνιακός Σάκος:", validators=[Optional()])
    contractions = StringField("Συστολές:", validators=[Optional()])
    cervical_dilation = StringField("Διαστολή Τραχήλου:", validators=[Optional()])
    cervical_effacement = StringField("Λέπτυνση Τραχήλου:", validators=[Optional()])
    arterial_pressure = StringField("Αρτηριακή Πίεση:", validators=[Optional()])
    temperature = FloatField("Θερμοκρασία (°C):", validators=[Optional()])
    sumphysial_fundal_height_sfh = FloatField("SFH (cm):", validators=[Optional()])
    comments = TextAreaField(
        "Σχόλια:", validators=[Optional()], render_kw={"class": "expanding-textarea"}
    )


class PregnancyHistoryXForm(FlaskForm):
    """Container for multiple antenatal visit entries"""

    entries = FieldList(FormField(PregnancyHistoryXEntryForm), min_entries=0)
