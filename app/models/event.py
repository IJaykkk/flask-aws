from app import db

class EventModel(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key = True)
    event_name = db.Column(db.String(120), unique = True, nullable = False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=false, index=True)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
