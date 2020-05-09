import os
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

api = Api(app)
db = SQLAlchemy(app)
jwt = JWTManager(app)

@app.before_first_request
def create_tables():
    db.create_all()

from app import views, tokens, models

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return models.RevokedTokenModel.is_jti_blacklisted(jti)

api.add_resource(tokens.UserRegistration, '/registration')
api.add_resource(tokens.UserLogin, '/login')
api.add_resource(tokens.UserLogoutAccess, '/logout/access')
api.add_resource(tokens.UserLogoutRefresh, '/logout/refresh')
api.add_resource(tokens.TokenRefresh, '/token/refresh')
api.add_resource(tokens.AllUsers, '/users')
api.add_resource(tokens.SecretResource, '/secret')
