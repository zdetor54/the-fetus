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
    
chatai = Blueprint('chatai', __name__)


@chatai.route('/chat')
def chat():
    return render_template('chat.html')


