from flask_login import UserMixin
from app import db
from app.utils import Jsonified


class User(UserMixin, db.Model, Jsonified):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    surname = db.Column(db.String(64), nullable=False)

    # def __init__(self, name: str, surname: str):
    #     self.name = name
    #     self.surname = surname

    def to_json(self):
        user_json = super().to_json()
        user_json.pop('is_active')
        user_json.pop('is_anonymous')
        user_json.pop('is_authenticated')
        return user_json

