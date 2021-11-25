from app import db


class Route(db.Model):
    __tablename__ = "route"

    id = db.Column(db.Integer, primary_key=True)
    start_datetime = db.Column(db.TIMESTAMP, nullable=False)
    end_datetime = db.Column(db.TIMESTAMP, nullable=False)

    order = db.Column(db.Integer, db.ForeignKey('order.id'))

    stretch = db.relationship("Stretch")
