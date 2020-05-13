from app import db
from app.models.event import EventModel


class GroupModel(db.Model):
    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)

    events = db.relationship('EventModel', backref='group', lazy=False)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def to_json(self, with_user=True):
        res = {
            'id': self.id,
            'name': self.name
        }
        if with_user:
            res.update({ 'users': list(map(lambda x: x.to_json(), self.users)) })
        return res
