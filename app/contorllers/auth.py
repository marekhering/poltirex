from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user
from werkzeug.security import generate_password_hash

from app.models import User
from app import db

auth = Blueprint('auth', __name__)


@auth.route('/')
def login():
    return render_template('login.html')


@auth.route('/register', methods=['POST'])
def register_post():
    name = request.form.get('name')
    surname = request.form.get('surname')
    user_login = request.form.get('login')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    if password != confirm_password:
        flash('Podane hasła się różnią')
        return redirect(url_for('auth.login'))

    print(User.query.filter_by(login=user_login).first())
    if User.query.filter_by(login=user_login).first():
        flash("Istnieje już użytkownik o nicku %s" % user_login)
        return redirect(url_for('auth.login'))

    password_hash = generate_password_hash(password, method='sha256')
    user = User(name=name, surname=surname, login=user_login, password=password_hash)
    db.session.add(user)
    db.session.commit()

    login_user(user)

    return redirect(url_for('main.profile'))
