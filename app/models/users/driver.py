from app import db
from .user import User


class Driver(User):
    __tablename__ = None
    __mapper_args__ = {
        'polymorphic_identity': 'driver'
    }

    truck = db.relationship("Truck", lazy='select', back_populates='driver', uselist=False)
