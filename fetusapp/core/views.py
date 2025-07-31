import os
from datetime import date, datetime, timedelta
from typing import Any, cast

import requests
from caldav import Calendar, DAVClient
from dotenv import load_dotenv
from flask import (
    Blueprint,
    Response,
    flash,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_user

from fetusapp.models import User

from ..users.forms import LoginForm

core = Blueprint("core", __name__)


def get_quote() -> list[dict[str, Any]]:
    default_quote: list[dict[str, Any]] = [
        {
            "content": "Wisdom is not a product of schooling but of the lifelong attempt to acquire it.",
            "author": "Albert Einstein",
        }
    ]

    try:
        response = requests.get("http://api.quotable.io/quotes/random", timeout=5)

        if response.status_code == 200:
            return [response.json()[0]]
        return default_quote
    except (requests.RequestException, KeyError, IndexError):
        return default_quote


def get_weather() -> dict[str, Any]:
    dotenv_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "..", "..", "keys.env"
    )
    load_dotenv(dotenv_path)
    meteo_api_key = os.getenv("METEO_API_KEY")

    default_weather = {
        "current": {
            "temperature": "--",
            "icon_num": 1,
        },
        "daily": {"data": [{"summary": "Could not fetch weather data."}]},
    }

    parameters = {
        "place_id": "athens",
        "sections": "current, daily",
        "language": "en",
        "units": "metric",
        "key": meteo_api_key,
    }

    try:
        weather_response = requests.get(
            f'https://www.meteosource.com/api/v1/free/point?place_id={parameters["place_id"]}&sections=current%2C%20daily&language=en&units=metric&key={parameters["key"]}'
        )
        if weather_response.status_code == 200:
            weather = cast(dict[str, Any], weather_response.json())
        else:
            weather = default_weather
    except (requests.RequestException, KeyError, ValueError):
        weather = default_weather

    return weather


def get_calendar_events(
    target_date: date = datetime.now().date(), days: int = 7
) -> list[Any]:
    # This is where the calendar events are fetched
    url = "https://caldav.icloud.com"
    username = "zdetor54@gmail.com"

    dotenv_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "..", "..", "keys.env"
    )
    load_dotenv(dotenv_path)
    password = os.getenv("APPLE_CAL_KEY")

    # Connect to the iCloud CalDAV server
    client = DAVClient(url, username=username, password=password)
    principal = client.principal()
    _ = principal.calendars()

    # Replace with the name of your desired calendar
    calendar_url = "https://p142-caldav.icloud.com:443/1101338323/calendars/75fec20324b34821c0cfae15e8a9cee826762747257294ea3bc5c2e6bd2ab65d/"
    calendar = Calendar(client, calendar_url)

    # Define the time range for the entire day
    start = datetime.combine(target_date, datetime.min.time())
    end = datetime.combine(target_date + timedelta(days), datetime.min.time())

    # Get events for the specified day
    events = calendar.date_search(start=start, end=end)

    return list(events)


@core.route("/", methods=["GET", "POST"])
@core.route("/<string:target_date>", methods=["GET", "POST"])
def index(target_date: str | None = None) -> Response:
    if target_date:
        try:
            current_date = datetime.strptime(target_date, "%Y-%m-%d")
        except ValueError:
            current_date = datetime.now()
    else:
        current_date = datetime.now()

    today = datetime.today()

    form = LoginForm()
    error_message = None
    messages = get_flashed_messages()

    weather = get_weather()

    quote = get_quote()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is not None and user.check_password(form.password.data):
            login_user(user)
            flash("Logged in successfully.")

            next_user = request.args.get("next")

            if next_user is None or not next_user[0] == "/":
                next_user = url_for("core.index")

            return redirect(next_user)
        else:
            error_message = "Incorrect username and/or password."

    try:
        events = get_calendar_events(target_date=current_date, days=1)
    except Exception:  # This is acceptable when you truly want to catch everything
        events = []

    return render_template(
        "index.html",
        form=form,
        active_page="index",
        error_message=error_message,
        quote=quote,
        weather=weather,
        messages=messages,
        calendar_events=events,
        current_date=current_date,
        today=today,
    )
