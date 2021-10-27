from app import db


class Truck(db.Model):
    __tablename__ = "truck"

    id = db.Column(db.Integer, primary_key=True)
    height = db.Column(db.Float, nullable=False)
    width = db.Column(db.Float, nullable=False)

    def __init__(self, height: float, width: float):
        self.height = height
        self.width = width

    def to_dict(self):
        return {
            "id": self.id,
            "height": self.height,
            "width": self.width
        }
