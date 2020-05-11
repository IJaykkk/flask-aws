from app import db

class PictureModel(db.Model):
    __tablename__ = 'pictures'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), index=True)
    klass = db.Column(db.String(10))
    is_bestshot = db.Column(db.Boolean, default=False)
    url = db.Column(db.String(240), nullable=False, index=True)


    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def to_json(self):
        return {
            'id': self.id,
            'class': self.klass,
            'is_bestshot': self.is_bestshot,
            'url': self.url
        }
