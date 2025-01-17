from app import db


class SubscriptionModel(db.Model):
    __tablename__ = 'subscriptions'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), primary_key=True)
    klass = db.Column(db.String(20), nullable=False)

    user = db.relationship('UserModel', back_populates='events')
    event = db.relationship('EventModel', back_populates='users')

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def to_json(self):
        res = {
            'people': False,
            'landscape': False
        }
        for k in self.klass.split('/'):
            res[k] = True
        return res
