import json
import os
import unicodedata
from datetime import date, datetime
from typing import Any, cast

import openai
import pandas as pd
from flask import (
    Blueprint,
    Response,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from fetusapp import app, csrf, db  # type: ignore[has-type]
from fetusapp.models import (
    GynHistory,
    HistoryMedical,
    HistoryObstetrics,
    HistoryObstetrics_x,
    Patient,
    PregnancyHistory,
    PregnancyHistory_x,
)

from .forms import (
    HistoryMedicalForm,
    HistoryObstetricsForm,
    HistoryObstetricsXForm,
    PregnancyHistoryForm,
    PregnancyHistoryXForm,
)

patients = Blueprint("patients", __name__)


def proper_case(value: str) -> str:
    return " ".join(word.capitalize() for word in value.split())


# Register the custom filter
app.jinja_env.filters["proper_case"] = proper_case  # type: ignore


# Define the custom filter
def zfill(value: Any, width: int = 4) -> str:
    return str(value).zfill(width)


# Register the custom filter
app.jinja_env.filters["zfill"] = zfill  # type: ignore


def extract_patient_details(text: str) -> dict[str, str]:
    openai.api_key = os.getenv("OPENAI_API_KEY")

    if not openai.api_key:
        # If no key configured, skip API and fall back to regex behavior
        return extract_patient_details_regex(text)

    # Define the prompt
    prompt = f"Extract the following types of PII from the following text: {text}"
    print(prompt)

    # Make the API call
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant extracting PII from text",
                },
                {
                    "role": "user",
                    "content": """Extract the following types of PII:
                                                - First name as "name",
                                                - Last name as "surname",
                                                - any phone numbers as "phone"
                                                - Ignore anything related to ODS, Δώδος, Δώδου, Αλιακιόζογλου.
                                                - I want the extract to be in a json format.
                                                - I only want one last name and/or one phone number to be extracted per prompt.
                                                - if there a attribute can't be found ignore the key

                                                The prompts are all in Greek and it's around obstetrics and gynecology appointments.

                                                Example: Λάμπρου Μαριάνα κυηση κινητό τηλέφωνο 6977221781-> {"name": "Μαριάνα", "surname": "Λαμπρου", "phone": "6977221781"}
                                                """
                    + prompt,
                },
            ],
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.5,
        )

        # Extract the PII from the response
        extracted_data = response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(e)
        extracted_data = ""
        return {"surname": "no quota"}

    # Parse the JSON response (if the model outputs JSON)
    try:
        extracted_data = json.loads(extracted_data)
        return cast(dict[str, str], extracted_data)
    except json.JSONDecodeError:
        return {}


def extract_patient_details_regex(text: str) -> dict:
    try:
        elements = text.split()
    except AttributeError:
        elements = []

    extracted_data = dict()
    for element in elements:
        try:
            int(element)
            extracted_data["phone"] = element
        except ValueError:
            if "name" not in extracted_data:
                extracted_data["name"] = element
            elif "surname" not in extracted_data:
                extracted_data["surname"] = element
            else:
                break
    return extracted_data


def normalize_text(text: str) -> str:
    return "".join(
        c
        for c in unicodedata.normalize("NFKD", text)
        if unicodedata.category(c) != "Mn"
    ).lower()


def normalize_json(json_data: dict) -> dict:
    for key, value in json_data.items():
        # if value is string, normalize it
        if isinstance(value, str):
            json_data[key] = normalize_text(value)
    return json_data


def filter_patients(patients: pd.DataFrame, search_parameters: dict) -> pd.DataFrame:
    # Create working copy of the dataframe
    search_row = pd.DataFrame([search_parameters]).iloc[0]

    if len(search_row) > 0:
        # Initialize matches as all True
        matches = pd.Series(True, index=patients.index)
        # Handle name matching if name is provided
        if "name" in search_row and not pd.isna(search_row["name"]):
            name_matches = (patients["first_name"] == search_row["name"]) | (
                patients["last_name"] == search_row["name"]
            )
            matches &= name_matches

        # Handle surname matching if surname is provided
        if "surname" in search_row and not pd.isna(search_row["surname"]):
            surname_matches = (patients["first_name"] == search_row["surname"]) | (
                patients["last_name"] == search_row["surname"]
            )
            matches &= surname_matches

        # Handle phone matching if phone is provided
        if "phone" in search_row and not pd.isna(search_row["phone"]):
            phone_matches = (
                (patients["home_phone"] == search_row["phone"])
                | (patients["mobile_phone"] == search_row["phone"])
                | (patients["alternative_phone"] == search_row["phone"])
            )
            matches &= phone_matches

    else:
        matches = pd.Series(False, index=patients.index)

    return patients[matches]


def search_patients_service(search_query: str) -> pd.DataFrame:
    """Service function for patient search logic"""
    if not search_query:
        return pd.DataFrame()

    search_parameters = extract_patient_details_regex(search_query)
    # Normalize the search parameters
    norm_search_parameters = normalize_json(search_parameters)

    all_patients = Patient.query.filter_by(is_active=True).all()
    patients_data = [
        {
            "id": p.id,
            "first_name": p.first_name,
            "last_name": p.last_name,
            "home_phone": p.home_phone,
            "mobile_phone": p.mobile_phone,
            "alternative_phone": p.alternative_phone,
        }
        for p in all_patients
    ]
    df_all_patients = pd.DataFrame(patients_data)

    df_all_patients["first_name"] = df_all_patients["first_name"].apply(normalize_text)
    df_all_patients["last_name"] = df_all_patients["last_name"].apply(normalize_text)

    patients_df = filter_patients(df_all_patients, norm_search_parameters)

    return patients_df


@patients.route("/patients", methods=["GET", "POST"])
def no_patient() -> Response:
    if not current_user.is_authenticated:
        flash("Συνδεθείτε για να δείτε τη σελίδα ασθενών.")
        return redirect(url_for("core.index", next=request.url))

    search_query = request.args.get("search_query")

    if request.method == "POST":
        search_query = request.form.get("search_query")

    patients = search_patients_service(search_query)

    if len(patients) > 0:
        # Convert DataFrame to list of dictionaries for template
        if isinstance(patients, pd.DataFrame):
            patients_list = patients.to_dict("records")
        else:
            patients_list = [
                {
                    "id": patient.id,
                    "first_name": patient.first_name,
                    "last_name": patient.last_name,
                    "mobile_phone": patient.mobile_phone,
                    "home_phone": patient.home_phone,
                    "alternative_phone": patient.alternative_phone,
                }
                for patient in patients
            ]
        return render_template(
            "patients.html",
            active_page="patient",
            patients=patients_list,
            has_searched=True,
        )
    return render_template(
        "patients.html", active_page="patient", patients=[], has_searched=True
    )


@patients.route("/patient", methods=["GET", "POST"])
def patient() -> Response:
    if not current_user.is_authenticated:
        flash("Συνδεθείτε για να δείτε τη σελίδα του ασθενή.")
        return redirect(url_for("core.index", next=request.url))

    patient_id = request.args.get("id")

    contact_fields = {
        "street_name": {"label": "Οδός", "type": "text"},
        "street_number": {"label": "Αριθμός", "type": "text"},
        "city": {"label": "Πόλη", "type": "text"},
        "postal_code": {"label": "Ταχυδρομικός Κωδικός", "type": "text"},
        "county": {"label": "Νομός", "type": "text"},
        "home_phone": {"label": "Σταθερό Τηλ", "type": "text"},
        "mobile_phone": {"label": "Κινητό Τηλ", "type": "text"},
        "alternative_phone": {"label": "Εναλλακτικό Τηλ", "type": "text"},
        "email": {"label": "Ε-mail", "type": "email"},
    }

    personal_data_fields = {
        "first_name": {"label": "Όνομα", "type": "text"},
        "last_name": {"label": "Επώνυμο", "type": "text"},
        "father_name": {"label": "Πατρώνυμο", "type": "text"},
        "marital_status": {
            "label": "Οικογενειακή Κατάσταση",
            "type": "select",
            "options": [
                {"value": "Έγγαμη", "label": "Έγγαμη"},
                {"value": "Άγαμη", "label": "Άγαμη"},
            ],
        },
        "nationality": {"label": "Εθνικότητα", "type": "text"},
        "occupation": {"label": "Επάγγελμα", "type": "text"},
    }

    partner_data_fields = {
        "spouse_name": {"label": "Ονοματεπώνυμο", "type": "text"},
        "spouse_occupation": {"label": "Επάγγελμα", "type": "text"},
    }

    if patient_id:
        patient = Patient.query.get(patient_id)
        history_medical_form = HistoryMedicalForm()
        history_obstetrics_form = HistoryObstetricsForm()
        history_obstetrics_x_form = HistoryObstetricsXForm()
        # get the medical history of the patient

        medical_history = HistoryMedical.query.filter_by(
            patient_id=patient_id, is_active=True
        ).first()

        if medical_history:
            history_medical_form = HistoryMedicalForm(obj=medical_history)

        try:
            medical_history_dict = medical_history.to_dict()
        except AttributeError:
            medical_history_dict = dict()

        obstetrics_history = HistoryObstetrics.query.filter_by(
            patient_id=patient_id, is_active=True
        ).first()

        if obstetrics_history:
            history_obstetrics_form = HistoryObstetricsForm(obj=obstetrics_history)

        try:
            obstetrics_history_dict = obstetrics_history.to_dict()
        except AttributeError:
            obstetrics_history_dict = dict()

        obstetrics_history_x = (
            HistoryObstetrics_x.query.filter_by(patient_id=patient_id, is_active=True)
            .order_by(HistoryObstetrics_x.year_of_birth.desc())
            .all()
        )

        # Prepare list of dicts using the model helper and populate FieldList directly
        obstetrics_history_x_dicts = [entry.to_dict() for entry in obstetrics_history_x]
        if obstetrics_history_x_dicts:
            for row in obstetrics_history_x_dicts:
                history_obstetrics_x_form.entries.append_entry(row)
        else:
            # ensure at least one empty form so template can render fields
            history_obstetrics_x_form.entries.append_entry()
            obstetrics_history_x_dicts = (
                history_obstetrics_x_form.entries.data
                if history_obstetrics_x_form.entries.data
                else [{}]
            )

        return render_template(
            "patient.html",
            active_page="patient",
            query_term=patient_id,
            patient=patient,
            now=date.today(),
            contact_fields=contact_fields,
            medical_history_form=history_medical_form,
            medical_history_dict=medical_history_dict,
            personal_data_fields=personal_data_fields,
            partner_data_fields=partner_data_fields,
            obstetrics_history_dict=obstetrics_history_dict,
            history_obstetrics_form=history_obstetrics_form,
            history_obstetrics_x_form=history_obstetrics_x_form,
            obstetrics_history_x_list=obstetrics_history_x_dicts,
        )

    return render_template(
        "patient.html",
        active_page="patient",
        now=date.today(),
        contact_fields=contact_fields,
        personal_data_fields=personal_data_fields,
        partner_data_fields=partner_data_fields,
        medical_history_form=history_medical_form,
    )


@patients.route("/patient/<int:patient_id>/tab/pregnancies")
def patient_tab_pregnancies(patient_id: int) -> Response:
    history_pregnancy_form = PregnancyHistoryForm()
    history_pregnancyX_form = PregnancyHistoryXForm()

    pregnancy_history = (
        PregnancyHistory.query.filter_by(patient_id=patient_id, is_active=True)
        .filter(PregnancyHistory.ter.isnot(None))
        .order_by(PregnancyHistory.ter.desc())
        .all()
    )
    pregnancy_history_dicts = [entry.to_dict() for entry in pregnancy_history]
    pregnancy_ids = [entry.id for entry in pregnancy_history]

    if pregnancy_history_dicts:
        for row in pregnancy_history_dicts:
            history_pregnancy_form.entries.append_entry(row)
    else:
        # ensure at least one empty form so template can render fields
        history_pregnancy_form.entries.append_entry()
        pregnancy_history_dicts = (
            history_pregnancy_form.entries.data
            if history_pregnancy_form.entries.data
            else [{}]
        )

    pregnancy_history_x = (
        PregnancyHistory_x.query.filter(
            PregnancyHistory_x.pregnancy_id.in_(pregnancy_ids),
            PregnancyHistory_x.is_active == True,  # noqa: E712
        )
        .order_by(PregnancyHistory_x.date_of_visit.desc())
        .all()
    )

    pregnancy_history_x_dicts = [entry.to_dict() for entry in pregnancy_history_x]
    if pregnancy_history_x_dicts:
        for row in pregnancy_history_x_dicts:
            history_pregnancyX_form.entries.append_entry(row)
    else:
        # ensure at least one empty form so template can render fields
        history_pregnancyX_form.entries.append_entry()
        pregnancy_history_x_dicts = (
            history_pregnancyX_form.entries.data
            if history_pregnancyX_form.entries.data
            else [{}]
        )
    print(pregnancy_history_x_dicts)
    patient = Patient.query.get(patient_id)
    return render_template(
        "patient_tabs/pregnancies.html",
        history_pregnancy_form=history_pregnancy_form,
        history_pregnancyX_form=history_pregnancyX_form,
        patient=patient,
    )


@patients.route("/patient/<int:patient_id>/tab/gynhistory")
def patient_tab_gynhistory(patient_id: int) -> Response:
    """Lazy-loaded Gynaecological history tab content."""
    patient = Patient.query.get(patient_id)
    # Optional: when ready, load actual records
    gyn_entries = (
        GynHistory.query.filter_by(patient_id=patient_id, is_active=True)
        .order_by(GynHistory.date_of_visit.desc())
        .all()
    )
    return render_template(
        "patient_tabs/history_gyn.html",
        patient=patient,
        gyn_entries=[e.to_dict() for e in gyn_entries] if gyn_entries else [],
    )


@patients.route("/api/patients", methods=["POST"])
@login_required
@csrf.exempt
def create_patient_api() -> Response:
    try:
        data = request.get_json()
        patient = Patient(
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            father_name=data.get("father_name"),
            date_of_birth=datetime.strptime(
                data.get("date_of_birth"), "%Y-%m-%d"
            ).date()
            if data.get("date_of_birth")
            else None,
            marital_status=data.get("marital_status"),
            nationality=data.get("nationality"),
            occupation=data.get("occupation"),
            street_name=data.get("street_name"),
            street_number=data.get("street_number"),
            city=data.get("city"),
            postal_code=data.get("postal_code"),
            county=data.get("county"),
            home_phone=data.get("home_phone"),
            mobile_phone=data.get("mobile_phone"),
            alternative_phone=data.get("alternative_phone"),
            email=data.get("email"),
            insurance=data.get("insurance"),
            insurance_comment=data.get("insurance_comment"),
            amka=data.get("amka"),
            spouse_name=data.get("spouse_name"),
            spouse_date_of_birth=datetime.strptime(
                data.get("spouse_date_of_birth"), "%Y-%m-%d"
            ).date()
            if data.get("spouse_date_of_birth")
            else None,
            spouse_occupation=data.get("spouse_occupation"),
            created_by=current_user.id,
            last_updated_by=current_user.id,
        )
        db.session.add(patient)
        db.session.commit()
        return jsonify({"success": True, "patient_id": patient.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400


@patients.route("/api/patients/<int:id>", methods=["PUT"])
@login_required
@csrf.exempt
def update_patient_api(id: int) -> Response:
    try:
        data = request.get_json()
        patient = Patient.query.get_or_404(id)

        date_fields = ["date_of_birth", "spouse_date_of_birth"]
        checkbox_fields = ["is_active"]

        # Update fields
        for key, value in data.items():
            if hasattr(patient, key):
                if key in date_fields:
                    if not value or value.strip() == "":
                        setattr(patient, key, None)
                    else:
                        try:
                            setattr(
                                patient,
                                key,
                                datetime.strptime(value, "%Y-%m-%d").date(),
                            )
                        except ValueError:
                            return (
                                jsonify(
                                    {
                                        "success": False,
                                        "error": f"Invalid date format for {key}",
                                    }
                                ),
                                400,
                            )
                elif key in checkbox_fields:
                    print(value)
                    if value:
                        setattr(patient, key, True)
                    else:
                        setattr(patient, key, False)
                else:
                    setattr(patient, key, value)

        # Update timestamps and user
        patient.last_updated_on = datetime.utcnow()
        patient.last_updated_by = current_user.id

        db.session.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400


@patients.route("/api/patients/<int:id>", methods=["DELETE"])
@login_required
@csrf.exempt
def delete_patient_api(id: int) -> Response:
    try:
        patient = Patient.query.get_or_404(id)
        patient.deactivate(user_id=current_user.id)
        return jsonify({"success": True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400


@patients.route("/api/patients/search", methods=["GET"])
def search_patients_api() -> Response:
    """API endpoint for patient search"""
    search_query = request.args.get("query")
    try:
        patients = search_patients_service(search_query)

        return jsonify(
            {
                "success": True,
                "count": len(patients),
                "data": patients.to_dict("records")
                if isinstance(patients, pd.DataFrame)
                else patients,
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@patients.route("/patients/search", methods=["GET"])
def search_patients_view() -> Response:
    """View for patient search results"""
    search_query = request.args.get("query")
    if not search_query:
        return render_template("patients.html", patients=[], has_searched=False)

    response = search_patients_service(search_query)

    if len(response) == 0:
        return render_template(
            "patients.html", active_page="patient", patients=[], has_searched=True
        )
    elif len(response) == 1:
        return redirect(
            url_for("patients.patient", active_page="patient", id=response.iloc[0].id)
        )
    else:
        return render_template(
            "patients.html",
            active_page="patient",
            patients=response.to_dict("records"),
            has_searched=True,
        )
