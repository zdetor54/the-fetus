from flask import render_template, request, Blueprint, flash, redirect, url_for, get_flashed_messages
from werkzeug.security import generate_password_hash,check_password_hash
from fetusapp import app,db,bcrypt
from flask_login import login_user,login_required,logout_user
from fetusapp.models import User
from .forms import RegistrationForm, DeleteUserForm, UpdateUserForm

users = Blueprint('users', __name__)


@users.route('/signup', methods=['GET', 'POST'])
def signup():

    form = RegistrationForm()
    delete_form = DeleteUserForm()
    update_form = UpdateUserForm()

    users = User.query.filter(User.is_active == True, User.username != 'admin').all()

    messages = get_flashed_messages()

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
            messages = get_flashed_messages()
            return redirect(url_for('users.signup', active_pill='register', messages=messages))
        else:
            flash('User not created. Please review errors in the form!')
            messages = get_flashed_messages()
            return render_template('signup.html', form=form, deleteform=delete_form, users=users, active_page='signup', active_pill='register', messages=messages)

    elif 'action' in request.form and request.form['action'] == 'delete':
        if delete_form.validate_on_submit():
            user = User.query.filter_by(username=delete_form.username.data).first()
            if user:
                user.is_active = False
                db.session.commit()
                flash('User deleted!')
                messages = get_flashed_messages()
                return redirect(url_for('users.signup', active_pill='delete', messages=messages))
            else:
                flash('User not found!')
                messages = get_flashed_messages()
            return redirect(url_for('users.signup', active_pill='delete', messages=messages))
        
    elif 'action' in request.form and request.form['action'] == 'update':
        if update_form.validate_on_submit():
            user = User.query.filter_by(username=update_form.username.data).first()
            if user and user.check_password(update_form.old_password.data):
                user.password_hash = generate_password_hash(update_form.password.data)
                db.session.commit()
                flash('User updated!')
                messages = get_flashed_messages()
                return redirect(url_for('users.signup', active_pill='update', messages=messages))
        else:
            user = User.query.filter_by(username=update_form.username.data).first()
            if user:
                if not user.check_password(update_form.old_password.data):
                    flash('Old password is incorrect!')

                if update_form.password.data != update_form.pass_confirm.data:
                    flash('Passwords do not match!')

                messages = get_flashed_messages()
                return redirect(url_for('users.signup', active_pill='update', messages=messages))
            else:
                flash('User not found!')
                messages = get_flashed_messages()
    
        return redirect(url_for('users.signup', active_pill='update', messages=messages))

    active_pill = request.args.get('active_pill', 'register')
    return render_template('signup.html', form=form, deleteform=delete_form, updateform = update_form, users=users, active_page='signup', active_pill=active_pill, messages=messages)

@users.route('/update_password', methods=['GET', 'POST'])
def update_password():
    update_form = UpdateUserForm()
    messages = get_flashed_messages()
    if 'action' in request.form and request.form['action'] == 'update':
        if update_form.validate_on_submit():
            user = User.query.filter_by(username=update_form.username.data).first()
            if user and user.check_password(update_form.old_password.data):
                user.password_hash = generate_password_hash(update_form.password.data)
                db.session.commit()
                flash('User updated!')
                return redirect(url_for('users.update_password'))
        else:
            user = User.query.filter_by(username=update_form.username.data).first()
            if not user.check_password(update_form.old_password.data):
                flash('Old password is incorrect!')

            if update_form.password.data != update_form.pass_confirm.data:
                flash('Passwords do not match!')
            
            return redirect(url_for('users.update_password'))



    return render_template('update_password.html', updateform = update_form, active_page='update_password', messages=messages)
    
@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('core.index'))
