from app import db

from app.models.picture import PictureModel
from app.models.subscription import SubscriptionModel

class EventModel(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    added_date = db.Column(db.DateTime, nullable=False)

    pictures = db.relationship('PictureModel', backref='event', lazy=True)
    users = db.relationship('SubscriptionModel', back_populates="event")

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def to_json(self, with_group=True, multi_pics=True, with_sub=None):
        res = {
            'id': self.id,
            'name': self.name,
            'added_date': self.added_date.strftime("%m/%d/%y")
        }

        if with_group:
            res.update({ 'group': self.group.to_json(with_user=False) })

        assert len(self.pictures) >= 1

        pictures = self.pictures if multi_pics else [self.pictures[0]]
        res.update({
            'pictures_size': len(self.pictures),
            'pictures': list(map(
                lambda x: x.to_json(),
                pictures))
        })

        # with_sub would be user_id if it exists
        if with_sub:
            sub = SubscriptionModel.query.filter_by(
                user_id=with_sub, event_id=self.id).first()

            if sub:
                tmp = sub.to_json()
            else:
                tmp = {
                    'people': False,
                    'landscape': False
                }

            res.update({ 'subscription': tmp })

        return res
