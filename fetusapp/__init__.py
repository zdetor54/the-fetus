import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config["SECRET_KEY"] = "mysecretkey"
bcrypt = Bcrypt(app)
app.jinja_env.globals.update(getattr=getattr)

#####################
# DATABASE SETUP ####
#####################
basedir = os.path.abspath(os.path.dirname(__file__))
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

csrf = CSRFProtect()
csrf.init_app(app)

#####################
# LOGIN CONFIGS #####
#####################

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "users.login"

from fetusapp.chatai.views import chatai  # noqa: E402
from fetusapp.core.views import core  # noqa: E402
from fetusapp.error_pages.handlers import error_pages  # noqa: E402
from fetusapp.patients.history_medical_views import medical_history  # noqa: E402
from fetusapp.patients.views import patients  # noqa: E402
from fetusapp.users.views import users  # noqa: E402

from . import models  # noqa: E402, F401

app.register_blueprint(core)
app.register_blueprint(error_pages)
app.register_blueprint(users)
app.register_blueprint(patients)
app.register_blueprint(medical_history)
app.register_blueprint(chatai)
