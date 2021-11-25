from app import db


class Order(db.Model):
    __tablename__ = "order"

    id = db.Column(db.Integer, primary_key=True)
    delivery_time = db.Column(db.TIMESTAMP, nullable=False)
    departure_place_lat = db.Column(db.Float, nullable=True)
    departure_place_lon = db.Column(db.Float, nullable=True)
    destination_place_lat = db.Column(db.Float, nullable=True)
    destination_place_lon = db.Column(db.Float, nullable=True)
    payload_weight = db.Column(db.Float, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    route = db.relationship("Route")
