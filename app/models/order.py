from app import db
from app.utils import Jsonified


class Order(db.Model, Jsonified):
    __tablename__ = "order"

    id = db.Column(db.Integer, primary_key=True)
    delivery_time = db.Column(db.TIMESTAMP, nullable=False)
    departure_place_lat = db.Column(db.Float, nullable=True)
    departure_place_lon = db.Column(db.Float, nullable=True)
    destination_place_lat = db.Column(db.Float, nullable=True)
    destination_place_lon = db.Column(db.Float, nullable=True)
    payload_weight = db.Column(db.Float, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    client = db.relationship("Client", lazy='select', back_populates="order", uselist=False)
    route = db.relationship("Route", lazy='select', back_populates="order", uselist=False)
