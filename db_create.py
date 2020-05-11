from app import db
from app.models import *

db.create_all()

print("DB created.")
