from flask import render_template, request, Blueprint
from fetusapp import app,db
from flask_login import login_user,login_required,logout_user
# from models import User
# from werkzeug.security import generate_password_hash, check_password_hash

core = Blueprint('core', __name__)

@core.route('/')
def index():
    return render_template('index.html', active_page='index')

# @core.route('/info')
# def info():
#     return render_template('info.html')

