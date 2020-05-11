from app import db

from app.models.picture import PictureModel

class EventModel(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False, index=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    added_date = db.Column(db.DateTime, nullable=False)

    pictures = db.relationship('PictureModel', backref='event', lazy=True)


    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def to_json(self, with_group=True, multi_pics=True):
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
            'pictures': list(map(
                lambda x: x.to_json(),
                pictures))
        })

        return res
