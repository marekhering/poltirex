from flask import Blueprint, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from app.models import Client, User
from app import db

auth = Blueprint('auth', __name__)


@auth.route('/login-post', methods=['POST'])
def login_post():
    login = request.form.get('login')
    password = request.form.get('password')

    user = User.query.filter_by(login=login).first()

    if not user:
        flash('Brak użytkownika o loginie %s' % login)
        return redirect(url_for('main.index'))

    if not check_password_hash(user.password, password):
        flash('Błędne hasło')
        return redirect(url_for('main.index'))

    login_user(user)
    return redirect(url_for('main.index'))


@auth.route('/register-post', methods=['POST'])
def register_post():
    name = request.form.get('name')
    surname = request.form.get('surname')
    login = request.form.get('login')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    if password != confirm_password:
        flash('Podane hasła się różnią')
        return redirect(url_for('main.index'))

    if User.query.filter_by(login=login).first():
        flash("Istnieje już użytkownik o nicku %s" % login)
        return redirect(url_for('main.index'))

    password_hash = generate_password_hash(password, method='sha256')
    client = Client(name=name, surname=surname, login=login, password=password_hash)
    db.session.add(client)
    db.session.commit()
    login_user(client)

    return redirect(url_for('main.index'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
