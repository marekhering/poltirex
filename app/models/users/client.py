from app import db
from .user import User


class Client(User):
    __tablename__ = None
    language = db.Column(db.String(2), default="PL")
    # order = db.relationship("Order", lazy='joined')

    __mapper_args__ = {
        'polymorphic_identity': 'client'
    }
