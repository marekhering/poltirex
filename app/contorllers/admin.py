from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash

from app import db
from app.models import Truck, User, Driver


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


@admin.route('/get-trucks', methods=['GET'])
def get_trucks():
    return jsonify([truck.to_json() for truck in Truck.query.all()])


@admin.route('/get-users', methods=['GET'])
def get_users():
    return jsonify([user.to_json() for user in User.query.all()])


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
