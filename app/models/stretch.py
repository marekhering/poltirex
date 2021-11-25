from app import db


class Stretch(db.Model):
    __tablename__ = "stretch"

    id = db.Column(db.Integer, primary_key=True)
    delivery_time = db.Column(db.TIMESTAMP, nullable=False)
    start_place_lat = db.Column(db.Float, nullable=True)
    start_place_lon = db.Column(db.Float, nullable=True)
    end_place_lat = db.Column(db.Float, nullable=True)
    end_place_lon = db.Column(db.Float, nullable=True)

    route_id = db.Column(db.Integer, db.ForeignKey('route.id'))
    truck_id = db.Column(db.Integer, db.ForeignKey('truck.id'))
