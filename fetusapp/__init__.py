import os

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)

# Load environment from keys.env at project root (one level up from this file)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(project_root, "keys.env"))

# Secrets & core config
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-insecure-change-me")
app.jinja_env.globals.update(getattr=getattr)

#####################
# DATABASE SETUP ####
#####################
basedir = os.path.abspath(os.path.dirname(__file__))

# If DATABASE_URL is provided (e.g., in keys.env or environment), prefer that.
db_uri = os.getenv("DATABASE_URL")
if db_uri:
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
else:
    # Check if running on Azure (Azure sets this environment variable)
    if os.environ.get("WEBSITE_HOSTNAME"):
        # Running on Azure - use persistent storage
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////home/data/data.sqlite"
    else:
        # Running locally - use your existing path
        basedir = os.path.abspath(os.path.dirname(__file__))
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
            basedir, "data.sqlite"
        )

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["WTF_CSRF_ENABLED"] = True  # Enable CSRF protection
app.config["WTF_CSRF_TIME_LIMIT"] = 3600  # Token timeout in seconds

db = SQLAlchemy(app)
Migrate(app, db)

csrf: CSRFProtect = CSRFProtect()
csrf.init_app(app)

#####################
# LOGIN CONFIGS #####
#####################

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "core.index"

from fetusapp.chatai.views import chatai  # noqa: E402
from fetusapp.core.views import core  # noqa: E402
from fetusapp.error_pages.handlers import error_pages  # noqa: E402
from fetusapp.patients.document_views import documents  # noqa: E402
from fetusapp.patients.history_gyn_views import gyn_history  # noqa: E402
from fetusapp.patients.history_medical_views import medical_history  # noqa: E402
from fetusapp.patients.history_obstetrics_views import (  # noqa: E402
    obstetrics_history,
    obstetrics_history_x,
)
from fetusapp.patients.pregnancy_views import pregnancy, pregnancy_x  # noqa: E402
from fetusapp.patients.views import patients  # noqa: E402
from fetusapp.users.views import users  # noqa: E402

from . import models  # noqa: E402, F401

app.register_blueprint(core)  # type: ignore[has-type]
app.register_blueprint(error_pages)
app.register_blueprint(users)
app.register_blueprint(patients)  # type: ignore[has-type]
app.register_blueprint(medical_history)  # type: ignore[has-type]
app.register_blueprint(obstetrics_history)  # type: ignore[has-type]
app.register_blueprint(obstetrics_history_x)  # type: ignore[has-type]
app.register_blueprint(pregnancy)  # type: ignore[has-type]
app.register_blueprint(pregnancy_x)  # type: ignore[has-type]
app.register_blueprint(gyn_history)  # type: ignore[has-type]
app.register_blueprint(documents)  # type: ignore[has-type]
app.register_blueprint(chatai)
