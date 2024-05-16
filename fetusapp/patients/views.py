from flask import render_template, request, Blueprint,flash,redirect,url_for, get_flashed_messages
from fetusapp import app,db
from flask_login import login_user,login_required,logout_user, current_user
from fetusapp.models import User

patients = Blueprint('patients', __name__)

@patients.route('/patients')
def no_patient():
    if not current_user.is_authenticated:
        flash('You need to be logged in to view the patient page.')
        return redirect(url_for('core.index'))
    return render_template('patient.html', active_page='patient')