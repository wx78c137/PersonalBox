from . import auth
from .. import db
from ..models import User
from .. import functions
from flask import render_template, redirect, url_for, request, flash
from .forms import LoginForm, RegisterForm, EditForm, ChangePassword
from flask_login import login_required, logout_user, login_user, current_user


@auth.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        email = login_form.email.data
        user = User.query.filter_by(email=email).first()
        if user is not None and user.verify_password(login_form.password.data):
            login_user(user)
            return redirect(url_for('main.root'))
        flash('Invalid username or password.')
    return render_template('login.html', login_form=login_form)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    while True:
        random = functions.RandomID()
        if User.query.filter_by(userkey=random).first() is not None:
            continue
        else:
            break
    if register_form.validate_on_submit():
        user = User(email=register_form.email.data,
                    username=register_form.username.data,
                    password=register_form.password.data, userkey=random)
        db.session.add(user)
        db.session.commit()
        if not functions.Installed(user.userkey):
            functions.Install(user.userkey)
        return redirect(url_for('auth.login'))
    return render_template('register.html', register_form=register_form)


@auth.route('/auth/profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    edit_form = EditForm()
    if edit_form.validate_on_submit():
        current_user.email = edit_form.email.data
        current_user.username = edit_form.username.data
        db.session.add(current_user)
        db.session.commit()
        return redirect(url_for('auth.edit_profile'))
    edit_form.email.data = current_user.email
    edit_form.username.data = current_user.username
    return render_template('edit_profile.html', edit_form=edit_form)


@auth.route('/auth/changepassword', methods=['GET', 'POST'])
def change_password():
    password_form = ChangePassword()
    if password_form.validate_on_submit():
        if current_user.verify_password(password_form.current_password.data):
            current_user.password = password_form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Your Password is changed')
            return redirect(url_for('auth.change_password'))
        else:
            flash('Your Password is incorrect')
            return redirect(url_for('auth.change_password'))
    return render_template('change_password.html', password_form=password_form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))
