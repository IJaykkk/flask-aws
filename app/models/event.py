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

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'added_date': self.added_date
        }
