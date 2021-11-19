from app import db


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100))
    password = db.Column(db.String(100))
    name = db.Column(db.String(64), nullable=False)
    surname = db.Column(db.String(64), nullable=False)

    def __init__(self, name: str, surname: str):
        self.name = name
        self.surname = surname
