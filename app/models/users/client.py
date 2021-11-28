from app import db
from .user import User


class Client(User):
    __tablename__ = None
    __mapper_args__ = {
        'polymorphic_identity': 'client'
    }

    language = db.Column(db.String(2), default="PL")
    order = db.relationship("Order", lazy='select', back_populates="client")
