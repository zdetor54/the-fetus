from flask import render_template, request, Blueprint, flash, redirect, url_for
from fetusapp import app,db
from flask_login import login_user,login_required,logout_user
from fetusapp.models import User
from .forms import RegistrationForm, DeleteUserForm

users = Blueprint('users', __name__)


@users.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    delete_form = DeleteUserForm()

    users = User.query.filter(User.is_active == True, User.username != 'admin').all()

    if 'action' in request.form and request.form['action'] == 'register':
        if form.validate_on_submit():
            user = User(
                username=form.username.data,
                password=form.password.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                is_admin=form.is_admin.data)
            db.session.add(user)
            db.session.commit()
            flash('User has been registered! They can now login!')
            return redirect(url_for('users.signup', active_pill='register'))
        else:
            flash('User not created. Please review errors in the form!')
            return render_template('signup.html', form=form, deleteform=delete_form, users=users, active_page='signup', active_pill='register')

    elif 'action' in request.form and request.form['action'] == 'delete':
        if delete_form.validate_on_submit():
            user = User.query.filter_by(username=delete_form.username.data).first()
            if user:
                user.is_active = False
                db.session.commit()
                flash('User deleted!')
                return redirect(url_for('users.signup', active_pill='delete'))
            else:
                flash('User not found!')
            return redirect(url_for('users.signup', active_pill='delete'))
    active_pill = request.args.get('active_pill', 'register')
    return render_template('signup.html', form=form, deleteform=delete_form, users=users, active_page='signup', active_pill=active_pill)
    
@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('core.index'))
