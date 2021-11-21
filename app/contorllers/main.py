from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.models import Client, Driver

main = Blueprint('main', __name__)


@main.route('/')
def index():
    if current_user.is_authenticated:
        if isinstance(current_user, Client):
            return redirect(url_for('main.order'))
        elif isinstance(current_user, Driver):
            return redirect(url_for('main.stretches'))
        else:
            return redirect(url_for('auth.logout'))
    else:
        return redirect(url_for('main.login'))


@main.route('/login')
def login():
    return render_template('login.html')


@main.route('/order')
@login_required
def order():
    return render_template('order.html', name=current_user.name)


@main.route('/stretches')
@login_required
def stretches():
    return render_template('stretches.html', name=current_user.name)
