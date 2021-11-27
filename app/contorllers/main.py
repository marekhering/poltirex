from datetime import datetime, timedelta

from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models import Client, Driver, Truck, Order, Stretch, Route
from app.utils import set_connection

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
    def find_closest_truck(a_lat, a_lon):
        closest_truck = None
        for processed_truck in Truck.query.all():
            truck_distance = dist_calc(processed_truck.position_lat, processed_truck.position_lon, a_lat, a_lon)
            if closest_truck is None or closest_truck[0] > truck_distance:
                closest_truck = (truck_distance, processed_truck)
        return closest_truck[1] if closest_truck is not None else None

    def plan_stretch(a_lat, a_lon, b_lat, b_lon, start_time=None, end_time=None):
        assert start_time is not None or end_time is not None
        dist = dist_calc(a_lat, a_lon, b_lat, b_lon)
        driving_time_hours = dist / Truck.MEAN_VELOCITY
        if start_time is None:
            start_time = end_time - timedelta(hours=driving_time_hours)
        else:  # end_time is None
            end_time = start_time + timedelta(hours=driving_time_hours)

        chosen_truck = find_closest_truck(a_lat, a_lon)
        return start_time, end_time, chosen_truck

    # Create order
    new_order = Order(
        delivery_time=datetime.strptime(request.form.get('delivery_time'), "%Y-%m-%d %H:%M"),
        departure_place_lat=float(request.form.get('depart_lat')),
        departure_place_lon=float(request.form.get('depart_lon')),
        destination_place_lat=float(request.form.get('dest_lat')),
        destination_place_lon=float(request.form.get('dest_lon')),
        payload_weight=request.form.get('weight'),
        user_id=current_user.id
    )

    # Create stretches
    middle_point_lat = (new_order.departure_place_lat + new_order.destination_place_lat) / 2
    middle_point_lon = (new_order.departure_place_lon + new_order.destination_place_lon) / 2

    stretch_2_start_time, stretch_2_end_time, stretch_2_truck = plan_stretch(middle_point_lat, middle_point_lon,
                                                                             new_order.destination_place_lat,
                                                                             new_order.destination_place_lon,
                                                                             end_time=new_order.delivery_time)

    if stretch_2_truck is None:
        flash("Brakuje dostępnych pojazdów", category='error')
        return render_template('order.html', name=current_user.name)

    stretch_1_start_time, stretch_1_end_time, stretch_1_truck = plan_stretch(new_order.departure_place_lat,
                                                                             new_order.departure_place_lon,
                                                                             middle_point_lat, middle_point_lon,
                                                                             end_time=stretch_2_start_time)
    if stretch_1_truck is None:
        flash("Brakuje dostępnych pojazdów", category='error')
        return render_template('order.html', name=current_user.name)

    # Create route
    new_route = Route(start_datetime=stretch_1_start_time, end_datetime=stretch_2_end_time)
    new_order.route = new_route

    stretch_1 = Stretch(start_datetime=stretch_1_start_time, end_datetime=stretch_1_end_time,
                        start_place_lat=new_order.departure_place_lat, start_place_lon=new_order.departure_place_lon,
                        end_place_lat=middle_point_lat, end_place_lon=middle_point_lon,
                        route_id=new_route.id, truck_id=stretch_1_truck.id)

    stretch_2 = Stretch(start_datetime=stretch_2_start_time, end_datetime=stretch_2_end_time,
                        start_place_lat=middle_point_lat, start_place_lon=middle_point_lon,
                        end_place_lat=new_order.destination_place_lat, end_place_lon=new_order.destination_place_lon,
                        route_id=new_route.id, truck_id=stretch_1_truck.id)

    new_route.stretch.append(stretch_1)
    new_route.stretch.append(stretch_2)
    stretch_1_truck.stretch.append(stretch_1)
    stretch_2_truck.stretch.append(stretch_2)

    db.session.add_all([stretch_1, stretch_2, new_route, new_order])
    db.session.commit()

    flash("Order created", category='success')
    return render_template('order.html', name=current_user.name)
