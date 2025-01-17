from passlib.hash import pbkdf2_sha256 as sha256

from app import db
from app.models.user_group import user_group
from app.models.subscription import SubscriptionModel


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(120), nullable=False)
    icon_url = db.Column(db.String(240), nullable=False)

    groups = db.relationship('GroupModel',
        secondary=user_group,
        lazy='subquery',
        backref=db.backref('users', lazy=True))
    events = db.relationship('SubscriptionModel', back_populates="user")

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def to_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'icon_url': self.icon_url
        }

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username = username).first()

    @classmethod
    def return_all(cls):
        return list(map(lambda x: x.to_json(), cls.query.all()))

    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {
                'message': '{} row(s) deleted'.format(num_rows_deleted)
            }
        except:
            return {
                'message': 'Deleting all the users went wrong'
            }
