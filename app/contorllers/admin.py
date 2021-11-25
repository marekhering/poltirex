from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash

from app import db
from app.models import Truck, User, Driver, Order, Route, Stretch


admin = Blueprint('admin', __name__)


@admin.route('/add-driver', methods=['POST'])
def add_driver():
    driver_json = request.get_json()
    name = driver_json['name']
    surname = driver_json['surname']
    login = driver_json['login']
    password = driver_json['password']
    password_hash = generate_password_hash(password, method='sha256')

    driver = Driver(name=name, surname=surname, login=login, password=password_hash)
    db.session.add(driver)
    db.session.commit()

    return "Driver has been added"


@admin.route('/add-truck', methods=['POST'])
def add_truck():
    truck_json = request.get_json()
    height = float(truck_json['height'])
    capacity = float(truck_json['capacity'])
    position_lat = float(truck_json['position_lat'])
    position_lon = float(truck_json['position_lon'])
    driver_id = int(User.query.filter_by(login=truck_json['driver']).first().id)

    truck = Truck(height=height, capacity=capacity, position_lat=position_lat, position_lon=position_lon, driver_id=driver_id)
    db.session.add(truck)
    db.session.commit()
    return "Truck has been added"


@admin.route('/get-users', methods=['GET'])
def get_users():
    return jsonify([user.to_json() for user in User.query.all()])


@admin.route('/get-orders', methods=['GET'])
def get_orders():
    return jsonify([order.to_json() for order in Order.query.all()])


@admin.route('/get-routes', methods=['GET'])
def get_routes():
    return jsonify([route.to_json() for route in Route.query.all()])


@admin.route('/get-stretches', methods=['GET'])
def get_stretches():
    return jsonify([stretch.to_json() for stretch in Stretch.query.all()])


@admin.route('/get-trucks', methods=['GET'])
def get_trucks():
    return jsonify([truck.to_json() for truck in Truck.query.all()])


@admin.route('/get-all-table-names', methods=['GET'])
def get_all_table_names():
    return jsonify(db.engine.table_names())


@admin.route('/reset-db', methods=['DELETE'])
def reset_db():
    db.drop_all()
    db.create_all()
    db.session.commit()
    return "Reset done"


@admin.route('/drop-db', methods=['DELETE'])
def drop_db():
    db.drop_all()
    db.session.commit()
    return "Drop done"
