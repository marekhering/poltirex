from app import db


class Order(db.Model):
    __tablename__ = "order"

    id = db.Column(db.Integer, primary_key=True)
    payload_weight = db.Column(db.Float, nullable=False)

    def __init__(self, payload_weight: float):
        self.payload_weight = payload_weight
