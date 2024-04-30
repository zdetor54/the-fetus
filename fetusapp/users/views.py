from flask import render_template, request, Blueprint, flash, redirect, url_for
from fetusapp import app,db
from flask_login import login_user,login_required,logout_user
from fetusapp.models import User
from .forms import RegistrationForm, LoginForm

users = Blueprint('users', __name__)


@users.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(
                    username=form.username.data,
                    password=form.password.data,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    is_admin=form.is_admin.data)
        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering! Now you can login!')
        return redirect(url_for('core.index'))
    else:
        flash('something went wrong!')
        return render_template('signup.html', form=form, active_page='signup')
    
@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('core.index'))
