from datetime import datetime, timedelta

from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models import Client, Driver, Truck, Order, Stretch, Route
from app.utils import set_connection
from app.logistic import execute_order

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
    return render_template('stretches.html', name=current_user.name, stretches=get_stretches())


def get_stretches(using_orm: bool = True):
    if using_orm is True:
        result = db.session.query(Stretch.start_datetime, Stretch.end_datetime, Stretch.start_place_lat,
                                  Stretch.start_place_lon, Stretch.end_place_lat, Stretch.end_place_lat, Client.name,
                                  Client.surname).select_from(Truck).join(Stretch).join(Route).join(Order).join(Client).\
            filter(Truck.driver_id == current_user.id).order_by(Stretch.start_datetime).all()
    else:
        connection = set_connection()
        cursor = connection.cursor()
        result = cursor.execute("""
        SELECT u.name, u.surname, u.date_of_birth, sm.value FROM truck t
        JOIN stretch s ON s.truck_id = t.id
        JOIN route r ON s.route_id = r.id
        JOIN order o ON r.order_id = o.id
        JOIN user u ON o.user_id = u.id 
        WHERE t.driver_id = '%s'
        ORDER BY s.start_datetime DESC
        LIMIT 10
        """ % current_user.id)
    return result

@main.route('/order-post', methods=['POST'])
@login_required
def order_post():
    result = insert_new_order()
    if result is True:
        flash("Order created", category='success')
        return render_template('order.html', name=current_user.name)
    else:
        flash("Brakuje dostępnych pojazdów", category='error')
        return render_template('order.html', name=current_user.name)


def insert_new_order(using_orm: bool = True) -> bool:
    new_order = Order(
        delivery_time=datetime.strptime(request.form.get('delivery_time'), "%Y-%m-%d %H:%M"),
        departure_place_lat=float(request.form.get('depart_lat')),
        departure_place_lon=float(request.form.get('depart_lon')),
        destination_place_lat=float(request.form.get('dest_lat')),
        destination_place_lon=float(request.form.get('dest_lon')),
        payload_weight=request.form.get('weight'),
        user_id=current_user.id
    )

    executed_order = execute_order(new_order)

    if executed_order is None:
        return False

    new_route, new_stretch_1, stretch_1_truck, new_stretch_2, stretch_2_truck = executed_order

    new_route.stretch.append(new_stretch_1)
    new_route.stretch.append(new_stretch_2)
    stretch_1_truck.stretch.append(new_stretch_1)
    stretch_2_truck.stretch.append(new_stretch_2)

    db.session.add_all([new_stretch_1, new_stretch_2, new_route, new_order])
    db.session.commit()
    return True
