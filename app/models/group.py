from app import db
from app.models.event import EventModel


class GroupModel(db.Model):
    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

    events = db.relationship('EventModel', backref='group', lazy=True)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'users': list(map(lambda x: x.to_json(), self.users))
        }

    @classmethod
    def find_by_username(cls, username):
        return list(map(
            lambda x: x.to_json(),
            cls.query.filter(cls.users.any(username=username)).all()
        ))
