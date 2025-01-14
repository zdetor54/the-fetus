from flask import render_template, request, Blueprint,flash,redirect,url_for, get_flashed_messages
from fetusapp import app,db
from flask_login import login_user,login_required,logout_user, current_user
from fetusapp.models import User,Patient
from .forms import PatientContactForm
import unicodedata
import os
from dotenv import load_dotenv


import openai
import json
import pandas as pd

patients = Blueprint('patients', __name__)

def proper_case(value):
    return ' '.join(word.capitalize() for word in value.split())

# Register the custom filter
app.jinja_env.filters['proper_case'] = proper_case

# Define the custom filter
def zfill(value, width=4):
    return str(value).zfill(width)

# Register the custom filter
app.jinja_env.filters['zfill'] = zfill


def extract_patient_details(text: str) -> dict:

    dotenv_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..', 'keys.env')
    load_dotenv(dotenv_path)


    openai.api_key = os.getenv("OPENAI_API_KEY")
    

    # Define the prompt
    prompt = f"Extract the following types of PII from the following text: {text}"
    print (prompt)

    # Make the API call
    try:    
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant extracting PII from text"},
                {"role": "user", "content": """Extract the following types of PII: 
                                                - First name as "name",
                                                - Last name as "surname", 
                                                - any phone numbers as "phone"
                                                - Ignore anything related to ODS, Δώδος, Δώδου, Αλιακιόζογλου. 
                                                - I want the extract to be in a json format.
                                                - I only want one last name and/or one phone number to be extracted per prompt.
                                                - if there a attribute can't be found ignore the key

                                                The prompts are all in Greek and it's around obstetrics and gynecology appointments.
                
                                                Example: Λάμπρου Μαριάνα κυηση κινητό τηλέφωνο 6977221781-> {"name": "Μαριάνα", "surname": "Λαμπρου", "phone": "6977221781"}
                                                """ + prompt},
            ],
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.5,
        )

        # Extract the PII from the response
        extracted_data = response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(e)
        extracted_data = ""
        return {"surname": "no quota"}

    # Parse the JSON response (if the model outputs JSON)
    try:
        extracted_data = json.loads(extracted_data)
        return extracted_data
    except json.JSONDecodeError:
        return {}

def extract_patient_details_regex(text: str) -> dict:
    elements = text.split()
    extracted_data = dict()
    for element in elements:
        try:
            int(element)
            extracted_data['phone'] = element
        except ValueError:
            if 'name' not in extracted_data:
                extracted_data['name'] = element
            else:
                extracted_data['surname'] = element
    print(elements)
    return extracted_data

def normalize_text(text):
    return ''.join(c for c in unicodedata.normalize('NFKD', text) if unicodedata.category(c) != 'Mn').lower()

def normalize_json(json_data:dict) -> dict:
    for key, value in json_data.items():
        # if value is string, normalize it
        if isinstance(value, str):
            json_data[key] = normalize_text(value)
    return json_data

def filter_patients(patients: pd.DataFrame, search_parameters: dict) -> pd.DataFrame:
    # Create working copy of the dataframe
    search_row =pd.DataFrame([search_parameters]).iloc[0]

    if len(search_row)>0:
        # Initialize matches as all True
        matches = pd.Series(True, index=patients.index)
        # Handle name matching if name is provided
        if 'name' in search_row and not pd.isna(search_row['name']):
            name_matches = (
                (patients['first_name'] == search_row['name']) |
                (patients['last_name'] == search_row['name'])
            )
            matches &= name_matches
        
        # Handle surname matching if surname is provided
        if 'surname' in search_row and not pd.isna(search_row['surname']):
            surname_matches = (
                (patients['first_name'] == search_row['surname']) |
                (patients['last_name'] == search_row['surname'])
            )
            matches &= surname_matches
        
        # Handle phone matching if phone is provided
        if 'phone' in search_row and not pd.isna(search_row['phone']):
            phone_matches = (
                (patients['home_phone'] == search_row['phone']) |
                (patients['mobile_phone'] == search_row['phone']) |
                (patients['alternative_phone'] == search_row['phone'])
            )
            matches &= phone_matches    
    
    else:
        matches = pd.Series(False, index=patients.index)

    return patients[matches]

def find_patient_TO_DELETE(search_query): # TO DELETE
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
            or (patient.home_phone and normalized_query in patient.home_phone) \
            or (patient.mobile_phone and normalized_query in patient.mobile_phone) \
            or (patient.alternative_phone and normalized_query in patient.alternative_phone):
            matching_patients.append(patient)
    patients = matching_patients
    return patients

@patients.route('/patients', methods=['GET', 'POST'])
def no_patient():
    if not current_user.is_authenticated:
        flash('You need to be logged in to view the patient page.')
        return redirect(url_for('core.index'))
    
    search_query = request.args.get('search_query')
    
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        
    patients = get_patients(search_query)

    if len(patients) > 0:
        # Convert DataFrame to list of dictionaries for template
        if isinstance(patients, pd.DataFrame):
            patients_list = patients.to_dict('records')
        else:
            patients_list = [
                {
                    'id': patient.id,
                    'first_name': patient.first_name,
                    'last_name': patient.last_name,
                    'mobile_phone': patient.mobile_phone,
                    'home_phone': patient.home_phone,
                    'alternative_phone': patient.alternative_phone
                }
                for patient in patients
            ]
        return render_template('patients.html', active_page='patient', patients=patients_list, has_searched=True)
    return render_template('patients.html', active_page='patient', patients=[], has_searched=True)

@patients.route('/patient', methods=['GET', 'POST'])
def patient():

    patient_id = request.args.get('id')

    if patient_id:
        patient = Patient.query.get(patient_id)
        return render_template('patient.html', active_page='patient',query_term=patient_id, patient=patient)
    
    return render_template('patient.html', active_page='patient')

@patients.route('/calendar_patient_search', methods=['GET'])
def calendar_patient_search():

    search_query = request.args.get('search_query')
    patients = get_patients(search_query)

    if len(patients) < 1:       # No patients found so no need to preserve the query string
        return redirect(url_for('patients.no_patient', search_query=search_query)) #TO DO: remove ', search_query=search_query'
    elif len(patients) == 1:
        return redirect(url_for('patients.patient', id=patients.iloc[0].id))
    
    return redirect(url_for('patients.no_patient', search_query=search_query))   # Multiple patients found, preserve the query string and show the search results


@patients.route('/get_patients/<string:search_query>', methods=['GET', 'POST'])
def get_patients(search_query: str) -> pd.DataFrame:
    """
    Get patients based on the search query provided.
    """

    # Extract the patient details from the search query
    search_parameters = extract_patient_details(search_query)
    
    # if the surname is found, and has the value "no quota", return an empty list
    if 'surname' in search_parameters and search_parameters['surname'] == "no quota":
        search_parameters = extract_patient_details_regex(search_query)
    # Normalize the search parameters
    norm_search_parameters = normalize_json(search_parameters)

    print(norm_search_parameters)
    

    # Fetch all patients and normalize their names for comparison
    all_patients = Patient.query.all()
    patients_data = [
        {
            'id': p.id,
            'first_name': p.first_name,
            'last_name': p.last_name,
            'home_phone': p.home_phone,
            'mobile_phone': p.mobile_phone,
            'alternative_phone': p.alternative_phone
        } 
        for p in all_patients
    ]
    df_all_patients = pd.DataFrame(patients_data)

    df_all_patients['first_name'] = df_all_patients['first_name'].apply(normalize_text)
    df_all_patients['last_name'] = df_all_patients['last_name'].apply(normalize_text)

    # Find the matching patients

    filtered_patients = filter_patients(df_all_patients, norm_search_parameters)
    print(f"The type of Filtered patients is: {type(filtered_patients)}")

    return filtered_patients