from app import db
from .user import User


class Client(User):
    __tablename__ = "client"
    language = db.Column(db.String(2), default="EN")
    order = db.relationship("Order", lazy='joined')
