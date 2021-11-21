from flask import Blueprint, jsonify
from app import db
from app.models import Truck, User


admin = Blueprint('admin', __name__)


@admin.route('/get-trucks', methods=['GET'])
def get_trucks():
    return jsonify([truck.to_json() for truck in Truck.query.all()])


@admin.route('/get-users', methods=['GET'])
def get_users():
    return jsonify([user.to_json() for user in User.query.all()])


@admin.route('/reset-db', methods=['DELETE'])
def reset_db():
    db.drop_all()
    db.create_all()
    db.session.commit()
    return "Reset done"


@admin.route('/get-all-table-names', methods=['GET'])
def get_all_table_names():
    return jsonify(db.engine.table_names())
