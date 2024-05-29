from flask import render_template, request, Blueprint,flash,redirect,url_for, get_flashed_messages
from fetusapp import app,db
from flask_login import login_user,login_required,logout_user, current_user
from fetusapp.models import User,Patient
from .forms import FindPatientForm
import unicodedata

import openai
import json

patients = Blueprint('patients', __name__)

def extract_cal_patient_details(text):

    openai.api_key = "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"

    # Define the prompt
    prompt = f"Extract the following types of PII from the following text: {text}"

    # Make the API call
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": """Extract the following types of PII: 
                                            - Last name, not first name 
                                            - any phone numbers
                                            - Ignore anything related to ODS, Δώδος, Δώδου, Αλιακιόζογλου. 
                                            - I want the extract to be in a json format.
                                            - I only want one last name and/or one phone number to be extracted per prompt.

                                            The prompts are all in Greek and it's around obstetrics and gynecology appointments.
             
                                            Example: Λάμπρου Μαριάνα κυηση -> {"surname": "Λαμπρου"}
                                            """},
            {"role": "user", "content": prompt},
        ],
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.5,
    )

    # Extract the PII from the response
    extracted_data = response['choices'][0]['message']['content'].strip()

    # Parse the JSON response (if the model outputs JSON)
    try:
        extracted_data = json.loads(extracted_data)
        return extracted_data
    except json.JSONDecodeError:
        return {}

def normalize_text(text):
    return ''.join(c for c in unicodedata.normalize('NFKD', text) if unicodedata.category(c) != 'Mn').lower()

def find_patient(search_query):
    patients = []


    normalized_query = normalize_text(search_query)

    # Fetch all patients and normalize their names for comparison
    all_patients = Patient.query.all()
    matching_patients = []

    for patient in all_patients:
        normalized_first_name = normalize_text(patient.first_name)
        normalized_last_name = normalize_text(patient.last_name)
        if (normalized_query in normalized_first_name) \
            or (normalized_query in normalized_last_name)\
            or (normalized_query in patient.home_phone)\
            or (normalized_query in patient.mobile_phone)\
            or (normalized_query in patient.alternative_phone):
            matching_patients.append(patient)

    patients = matching_patients
    return patients

@patients.route('/patients', methods=['GET', 'POST'])
def no_patient():
    if not current_user.is_authenticated:
        flash('You need to be logged in to view the patient page.')
        return redirect(url_for('core.index'))
    


    elif request.method == 'POST':
            search_query = request.form.get('search_query')
            print(search_query)
            patients = find_patient(search_query)
            if patients is not None:
                for patient in patients:
                    print(patient)
                return render_template('patients.html', active_page='patient', patients=patients, has_searched=True)
            return render_template('patients.html', active_page='patient', patients=patients, has_searched=True)
    
    return render_template('patients.html', active_page='patient')

@patients.route('/patient_search', methods=['GET'])
def cal_patient_search():
    query_term = 'no query'
    query = request.args.get('query')
    patient = extract_cal_patient_details(query)
    print(patient)
    try:
        query_term = patient['phone']
        patients = find_patient(query_term)
        if patients is  None:
            return render_template('patients.html', active_page='patient', patients=patients, has_searched=True)
        elif len(patients) == 1:
            return render_template('patient.html', active_page='patient', query_term=query_term)
        else:
            return render_template('patients.html', active_page='patient', patients=patients, has_searched=True)
        
    except:
        try:
            query_term = patient['surname']
            patients = find_patient(query_term)
            if patients is  None:
                return render_template('patients.html', active_page='patient', patients=patients, has_searched=True)
            elif len(patients) == 1:
                return render_template('patient.html', active_page='patient', query_term=query_term)
            else:
                return render_template('patients.html', active_page='patient', patients=patients, has_searched=True)
        except:
            query_term = "No patient data found"

    return render_template('patients.html', active_page='patient')