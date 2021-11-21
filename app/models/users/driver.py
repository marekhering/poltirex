from .user import User


class Driver(User):
    __tablename__ = None
    __mapper_args__ = {
        'polymorphic_identity': 'driver'
    }
