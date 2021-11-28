from app import db
from app.utils import Jsonified


class Route(db.Model, Jsonified):
    __tablename__ = "route"

    id = db.Column(db.Integer, primary_key=True)
    start_datetime = db.Column(db.TIMESTAMP, nullable=False)
    end_datetime = db.Column(db.TIMESTAMP, nullable=False)

    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))

    stretch = db.relationship("Stretch", lazy='joined', back_populates='route')
    order = db.relationship("Order", lazy='select', back_populates="route", uselist=False)
