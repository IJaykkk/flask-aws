from app import db
from app.models.user import UserModel
from app.models.group import GroupModel
from app.models.event import EventModel
from app.models.revoked_token import RevokedTokenModel

db.create_all()

print("DB created.")
