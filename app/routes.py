from flask import jsonify, request, render_template

from app import app, db
from .models import Truck


@app.route('/', methods=['GET'])
def hello_world():
    return jsonify(hello="world")


@app.route('/get-truck/<truck_id>', methods=['GET'])
def get_truck(truck_id: str):
    assert db.session.query(Truck).get(int(truck_id)) is not None, "No truck with given id"
    return jsonify(db.session.query(Truck).get(int(truck_id)).to_dict())


@app.route('/get-all-trucks', methods=['GET'])
def get_all_trucks():
    return jsonify([truck.to_dict() for truck in Truck.query.all()])


@app.route('/get-trucks-view', methods=['GET'])
def get_trucks_view():
    return render_template('index.html', trucks=[truck.to_dict() for truck in Truck.query.all()])


@app.route('/add-truck', methods=['POST'])
def add_truck():
    truck_json = request.get_json()
    assert all([key in truck_json for key in ['height', 'width']])
    try:
        db.session.add(Truck(truck_json['height'], truck_json['width']))
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        raise exc
    return "Truck added"


@app.route('/delete-truck/<truck_id>', methods=['DELETE'])
def delete_truck(truck_id: str):
    assert db.session.query(Truck).get(int(truck_id)) is not None, "No truck with given id"
    try:
        Truck.query.filter_by(id=int(truck_id)).delete()
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        raise exc
    return "Truck deleted"


@app.route('/update-truck-width/<truck_id>/<new_width>', methods=['PATCH'])
def update_truck_width(truck_id: str, new_width: str):
    assert db.session.query(Truck).get(int(truck_id)) is not None, "No truck with given id"
    try:
        Truck.query.filter_by(id=int(truck_id)).update({Truck.width: int(new_width)})
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        raise exc
    return "Truck updated"
