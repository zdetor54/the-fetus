from flask import render_template, request, Blueprint,flash,redirect,url_for
from fetusapp import app,db
from flask_login import login_user,login_required,logout_user
from fetusapp.models import User
from fetusapp.users.views import users
from ..users.forms import RegistrationForm, LoginForm
# from werkzeug.security import generate_password_hash, check_password_hash

core = Blueprint('core', __name__)

@core.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    error_message = None
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

    return render_template('index.html', form=form, active_page='index', error_message=error_message)


