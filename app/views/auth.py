from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user


from ..models.models import User
from .. import db
from ..util.form_validation import ChangeSite, ChangeBuilding, ChangeRoom, ChangePassword, ChangeEmail

auth = Blueprint('auth', __name__)

@auth.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html', name=current_user.name)

@auth.route('/register')
def register():
    print("register")
    return render_template('auth/register.html')
    
@auth.route('/register', methods=['POST'])
def register_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    site = request.form.get('site')
    building = request.form.get('building')
    room = request.form.get('room')

    user = User.query.filter_by(email=email).first()
    if user:
        flash('Email address is already registered' , 'danger')
        return redirect(url_for('auth.register'))
    
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'), site=site, building=building, room=room)
    try:
        db.session.add(new_user)
        db.session.commit()
    except:
        return 'Unable to add the user to database.'
    flash('Account has been registered. Please log in:', 'success')
    return redirect(url_for('auth.login'))

@auth.route('/login', methods=['GET'])
def login():
    print("Login")
    return render_template('auth/login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.', 'danger')
        return redirect(url_for('auth.login'))
    login_user(user, remember=remember)
    return redirect(url_for('auth.profile'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/change-site', methods=['GET', 'POST'])
@login_required
def change_site():
    change_site_form = ChangeSite()
    if request.method == 'POST':
        if change_site_form.validate_on_submit():
            user = current_user
            user.site = change_site_form.site.data
            db.session.add(user)
            db.session.commit()
            flash('Your site has been changed.', 'success')
            return redirect(url_for('auth.profile'))
    return render_template('auth/change-site.html', site=current_user.site, change_site_form=change_site_form)

@auth.route('/change-building', methods=['GET', 'POST'])
@login_required
def change_building():
    change_building_form = ChangeBuilding()
    if request.method == 'POST':
        if change_building_form.validate_on_submit():
            user = current_user
            user.building = change_building_form.building.data
            db.session.add(user)
            db.session.commit()
            flash('Your buulding has been changed.', 'success')
            return redirect(url_for('auth.profile'))
    return render_template('auth/change-building.html', building=current_user.building, change_building_form=change_building_form)

@auth.route('/change-room', methods=['GET', 'POST'])
@login_required
def change_room():
    change_room_form = ChangeRoom()
    if request.method == 'POST':
        if change_room_form.validate_on_submit():
            user = current_user
            user.room = change_room_form.room.data
            db.session.add(user)
            db.session.commit()
            flash('Your room has been changed.', 'success')
            return redirect(url_for('auth.profile'))
    return render_template('auth/change-room.html', room=current_user.room, change_room_form=change_room_form)

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    change_password_form = ChangePassword()
    if request.method == 'POST':
        if change_password_form.validate_on_submit():
            user = current_user
            user.password = generate_password_hash(change_password_form.password.data, method='sha256')
            db.session.add(user)
            db.session.commit()
            flash('Your password has been changed.', 'success')
            return redirect(url_for('auth.profile'))
    return render_template('auth/change-password.html', change_password_form=change_password_form)

@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email():
    change_email_form = ChangeEmail()
    if request.method == 'POST':
        if change_email_form.validate_on_submit():
            try:
                user_check = User.query.filter_by(email=change_email_form.email.data).first()
                if user_check is None:
                    user = current_user
                    user.email = change_email_form.email.data
                    db.session.add(user)
                    db.session.commit()
                    flash('Your email has been changed', 'success')
                    return redirect(url_for('auth.profile'))
                else:
                    db.session.rollback()
                    flash('Sorry, that email already exists!', 'danger')
                    return render_template('auth/change-email.html', change_email_form=change_email_form)
            except IntegrityError:
                db.session.rollback()
                flash('Error! That email already exists!', 'danger')
    return render_template('auth/change-email.html', email=current_user.email, change_email_form=change_email_form)