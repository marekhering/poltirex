from app import db
from app.utils import Jsonified


class Truck(db.Model, Jsonified):
    __tablename__ = "truck"

    id = db.Column(db.Integer, primary_key=True)
    height = db.Column(db.Float, nullable=False)
    width = db.Column(db.Float, nullable=False)

    driver_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    stretch = db.relationship("Stretch")
