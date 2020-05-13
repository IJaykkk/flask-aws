import os
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
cors = CORS(app, resources={r"/*": {"origins": "*"}})
api = Api(app)
db = SQLAlchemy(app)
jwt = JWTManager(app)

from app.controllers import (tokens, users, groups, events, pictures)
from app.models.revoked_token import RevokedTokenModel

@app.teardown_appcontext
def teardown_appcontext(response_or_exc):
    db.session.remove()

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return RevokedTokenModel.is_jti_blacklisted(jti)

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user['username']

# Token
api.add_resource(tokens.UserRegistration, '/registration')
api.add_resource(tokens.UserLogin, '/login')
api.add_resource(tokens.UserLogoutAccess, '/logout/access')
api.add_resource(tokens.UserLogoutRefresh, '/logout/refresh')
api.add_resource(tokens.TokenRefresh, '/token/refresh')

# Users
api.add_resource(users.UserListResource, '/users')

# Groups
api.add_resource(groups.GroupListResource, '/groups')
api.add_resource(groups.GroupResource, '/group/<int:group_id>')

# Events
api.add_resource(events.EventListResource, '/events')
api.add_resource(events.EventResource, '/event/<int:event_id>')
api.add_resource(events.PictureListResource, '/event/<int:event_id>/pictures')
api.add_resource(events.SubscriptionResource, '/event/<int:event_id>/subscriptions')

# Pictures
api.add_resource(pictures.PictureBestshotResource, '/pictures/is_bestshot')
api.add_resource(pictures.PictureClassResource, '/pictures/class')


if __name__ == '__main__':
    app.run(host='0.0.0.0')

