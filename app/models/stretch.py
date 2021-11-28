from app import db
from app.utils import Jsonified


class Stretch(db.Model, Jsonified):
    __tablename__ = "stretch"

    id = db.Column(db.Integer, primary_key=True)
    start_datetime = db.Column(db.TIMESTAMP, nullable=False)
    end_datetime = db.Column(db.TIMESTAMP, nullable=False)
    start_place_lat = db.Column(db.Float, nullable=True)
    start_place_lon = db.Column(db.Float, nullable=True)
    end_place_lat = db.Column(db.Float, nullable=True)
    end_place_lon = db.Column(db.Float, nullable=True)

    route_id = db.Column(db.Integer, db.ForeignKey('route.id'))
    truck_id = db.Column(db.Integer, db.ForeignKey('truck.id'))

    route = db.relationship("Route", lazy='select', back_populates='stretch')
    truck = db.relationship("Truck", lazy='select', back_populates='stretch')
