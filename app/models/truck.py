from app import db
from app.utils import Jsonified


class Truck(db.Model, Jsonified):
    MEAN_VELOCITY = 0.5  # Degree/Hour

    __tablename__ = "truck"

    id = db.Column(db.Integer, primary_key=True)
    height = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Float, nullable=False)
    position_lat = db.Column(db.Float, nullable=False)
    position_lon = db.Column(db.Float, nullable=False)

    driver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    stretch = db.relationship("Stretch")
