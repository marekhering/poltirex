from typing import Tuple, Optional
from datetime import datetime, timedelta
import random
import time

from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from app import db
from app.models import Client, Driver, Truck, Order, Stretch, Route
from app.utils import set_cursor, set_connection
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
    return render_template('stretches.html', name=current_user.name, stretches=get_stretches(current_user.id)[0])


@main.route('/test-stretches/<no_test>/<user_id>')
def test_stretches(no_test: int, user_id: int):
    def perform_test(using_orm: bool):
        sum_time = 0
        for _ in range(int(no_test)):
            sum_time += get_stretches(int(user_id), using_orm=using_orm)[1]
        return sum_time / int(no_test)

    return jsonify({
        'mean_time_using_orm': perform_test(True),
        'mean_time_using_sql': perform_test(False)
    })


def get_stretches(user_id: int, using_orm: bool = False):
    if using_orm is True:
        t0 = time.time()
        result = db.session.query(Stretch.start_datetime, Stretch.end_datetime, Stretch.start_place_lat,
                                  Stretch.start_place_lon, Stretch.end_place_lat, Stretch.end_place_lat, Client.name,
                                  Client.surname).select_from(Truck).join(Stretch).join(Route).join(Order).join(Client).\
            filter(Truck.driver_id == user_id).order_by(Stretch.start_datetime).all()
        t1 = time.time() - t0
    else:
        cursor = set_cursor()
        t0 = time.time()
        cursor.execute("""
        SELECT s.start_datetime, s.end_datetime, s.start_place_lat, s.start_place_lon, s.end_place_lat, s.end_place_lat, 
        u.name, u.surname
        FROM truck t
        JOIN stretch s ON s.truck_id = t.id
        JOIN route r ON s.route_id = r.id
        JOIN "order" o ON r.order_id = o.id
        JOIN "user" u ON o.user_id = u.id
        WHERE t.driver_id = '%s'
        ORDER BY s.start_datetime
        """ % user_id)
        t1 = time.time() - t0

        result = cursor.fetchall()
    return result, t1


@main.route('/order-post', methods=['POST'])
@login_required
def order_post():
    result = insert_new_order_form(current_user.id)
    if result is True:
        flash("Order created", category='success')
        return render_template('order.html', name=current_user.name)
    else:
        flash("Brakuje dostępnych pojazdów", category='error')
        return render_template('order.html', name=current_user.name)


@main.route('/test-order/<no_test>/<user_id>')
def test_oder(no_test: int, user_id: int):
    test_order_dict = {
        'delivery_time': datetime.strptime("2022-01-01 12:00", "%Y-%m-%d %H:%M"),
        'depart_lat': 50,
        'depart_lon': 20,
        'dest_lat': 51,
        'dest_lon': 21,
        'weight': 100,
    }

    def perform_test(using_orm: bool):
        sum_time = 0
        for _ in range(int(no_test)):
            test_order_dict['delivery_time'] += timedelta(days=(random.randint(1, 100)))
            sum_time += insert_new_order(test_order_dict, int(user_id), using_orm=using_orm)[1]
        return sum_time / int(no_test)

    return jsonify({
        'mean_time_using_orm': perform_test(True),
        'mean_time_using_sql': perform_test(False)
    })


def insert_new_order_form(user_id: int) -> bool:
    return insert_new_order({
        'delivery_time': datetime.strptime(request.form.get('delivery_time'), "%Y-%m-%d %H:%M"),
        'depart_lat': float(request.form.get('depart_lat')),
        'depart_lon': float(request.form.get('depart_lon')),
        'dest_lat': float(request.form.get('dest_lat')),
        'dest_lon': float(request.form.get('dest_lon')),
        'weight': request.form.get('weight'),
    }, user_id, using_orm=True)[0]


def insert_new_order(order_dict: dict, user_id: int, using_orm: bool = True) -> Tuple[bool, Optional[float]]:
    new_order = Order(
        delivery_time=order_dict['delivery_time'],
        departure_place_lat=order_dict['depart_lat'],
        departure_place_lon=order_dict['depart_lon'],
        destination_place_lat=order_dict['dest_lat'],
        destination_place_lon=order_dict['dest_lon'],
        payload_weight=order_dict['weight'],
        user_id=user_id
    )

    executed_order = execute_order(new_order)

    if executed_order is None:
        return False, 0

    new_route, new_stretch_1, stretch_1_truck, new_stretch_2, stretch_2_truck = executed_order

    new_route.stretch.append(new_stretch_1)
    new_route.stretch.append(new_stretch_2)
    stretch_1_truck.stretch.append(new_stretch_1)
    stretch_2_truck.stretch.append(new_stretch_2)

    if using_orm:
        t0 = time.time()
        db.session.add_all([new_stretch_1, new_stretch_2, new_route, new_order])
        db.session.commit()
    else:
        connection = set_connection()
        cursor = connection.cursor()

        t0 = time.time()
        cursor.execute("""
            INSERT INTO "order" (delivery_time, departure_place_lat, departure_place_lon, destination_place_lat, 
            destination_place_lon, payload_weight, user_id) 
            VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s') RETURNING id
            """ % (new_order.delivery_time, new_order.departure_place_lat, new_order.departure_place_lon,
                   new_order.destination_place_lat, new_order.destination_place_lon,
                   new_order.payload_weight, new_order.user_id))
        new_order_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO route (start_datetime, end_datetime, order_id) 
            VALUES ('%s', '%s', '%s') RETURNING id
            """ % (new_route.start_datetime, new_route.end_datetime, new_order_id))
        new_route_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO stretch (start_datetime, end_datetime, start_place_lon, start_place_lat, end_place_lon, 
            end_place_lat, route_id, truck_id)
            VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s'),
                   ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')
            """ % (new_stretch_1.start_datetime, new_stretch_1.end_datetime, new_stretch_1.start_place_lat,
                   new_stretch_1.start_place_lon, new_stretch_1.end_place_lat, new_stretch_1.end_place_lon,
                   new_route_id, new_stretch_1.truck_id,
                   new_stretch_2.start_datetime, new_stretch_2.end_datetime, new_stretch_2.start_place_lat,
                   new_stretch_2.start_place_lon, new_stretch_2.end_place_lat, new_stretch_2.end_place_lon,
                   new_route_id, new_stretch_2.truck_id,
                   ))

        connection.commit()
    return True, time.time() - t0
