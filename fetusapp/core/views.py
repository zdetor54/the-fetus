from flask import render_template, request, Blueprint,flash,redirect,url_for, get_flashed_messages
from fetusapp import app,db
from flask_login import login_user,login_required,logout_user
from fetusapp.models import User
from fetusapp.users.views import users
from ..users.forms import RegistrationForm, LoginForm
import os
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta

from caldav import DAVClient, Calendar
    
core = Blueprint('core', __name__)

def get_calendar_events(target_date = datetime.now().date(), days=7):
     # This is where the calendar events are fetched
    url = "https://caldav.icloud.com"
    username = "zdetor54@gmail.com"

    dotenv_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..', 'keys.env')
    print(dotenv_path)
    load_dotenv(dotenv_path)
    password = os.getenv("APPLE_CAL_KEY")

    # Connect to the iCloud CalDAV server
    client = DAVClient(url, username=username, password=password)
    principal = client.principal()
    calendars = principal.calendars()


    # Replace with the name of your desired calendar
    calendar_url = "https://p142-caldav.icloud.com:443/1101338323/calendars/75fec20324b34821c0cfae15e8a9cee826762747257294ea3bc5c2e6bd2ab65d/"
    calendar = Calendar(client, calendar_url)
    print(f"Calendar: {calendar}")

    # Define the time range for the entire day
    start = datetime.combine(target_date, datetime.min.time())
    end = datetime.combine(target_date + timedelta(days), datetime.min.time())

    # Get events for the specified day
    events = calendar.date_search(start=start, end=end)

    return events

@core.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    error_message = None
    messages = get_flashed_messages()

    dotenv_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..', 'keys.env')
    load_dotenv(dotenv_path)  
    meteo_api_key = os.getenv("METEO_API_KEY")
    
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

            next_user = request.args.get('next')

            if next_user == None or not next[0] == '/':
                next_user = url_for('core.index')

            return redirect(next_user)
        else:
            error_message = 'Incorrect username and/or password.'

        # Print event details


     # Specify the day you want to get events for
    target_date = datetime(2024, 6, 4)  # Replace with your desired date

    try:
        events = get_calendar_events(target_date = target_date, days=2)
    except:
        events = []
    # if events:
    #     for event in events:
    #         vevent = event.vobject_instance.vevent
    #         print(f"UID: {vevent.uid.value if hasattr(vevent, 'uid') else 'No UID'}")
    #         print(f"Summary: {vevent.summary.value if hasattr(vevent, 'summary') else 'No Summary'}")
    #         print(f"Description: {vevent.description.value if hasattr(vevent, 'description') else 'No Description'}")
    #         print(f"Start: {vevent.dtstart.value if hasattr(vevent, 'dtstart') else 'No Start Date'}")
    #         print(f"End: {vevent.dtend.value if hasattr(vevent, 'dtend') else 'No End Date'}")
    #         print("---")


    return render_template('index.html', form=form, active_page='index', error_message=error_message, quote=quote, weather=weather, messages=messages, calendar_events=events)


