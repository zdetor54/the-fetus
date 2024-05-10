from flask import render_template, request, Blueprint,flash,redirect,url_for, get_flashed_messages
from fetusapp import app,db
from flask_login import login_user,login_required,logout_user
from fetusapp.models import User
from fetusapp.users.views import users
from ..users.forms import RegistrationForm, LoginForm
# from werkzeug.security import generate_password_hash, check_password_hash
import requests

core = Blueprint('core', __name__)

@core.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    error_message = None
    messages = get_flashed_messages()

    meteo_api_key = 'x3i7ycpbrubvoi35v0obzlc93ihhb2yumy0ylp7e'
    default_weather = {
            'current': {
                'temperature': '--',
                'icon_num': 1,                
            },
            'daily': {'data': [{'summary':'Could not fetch weather data.'}]}
        }

    parameters = {
        'place_id': 'athens',
        'sections': 'current, daily',
        'language': 'en',
        'units': 'metric',
        'key': meteo_api_key
    }

    try: 
        weather_response = requests.get(f'https://www.meteosource.com/api/v1/free/point?place_id={parameters["place_id"]}&sections=current%2C%20daily&language=en&units=metric&key={parameters["key"]}')
        if weather_response.status_code == 200:
            weather = weather_response.json()
        else:
            weather = default_weather
    except:
        weather = default_weather

    default_quote = [{
        'content': 'Could not fetch quote data.',
        'author': 'Unknown'
    }]
    try:
        response = requests.get('https://api.quotable.io/quotes/random')
        if response.status_code == 200:
            quote = response.json()
        else:
            quote = default_quote
    except:
        quote = default_quote

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        

        if user is not None and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully.')

            next = request.args.get('next')

            if next == None or not next[0] == '/':
                next = url_for('core.index')

            return redirect(next)
        else:
            error_message = 'Incorrect username and/or password.'

    return render_template('index.html', form=form, active_page='index', error_message=error_message, quote=quote, weather=weather, messages=messages)


