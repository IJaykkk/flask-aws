from datetime import datetime
from functools import wraps

from flask import g
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)
from flask_restful import Resource, reqparse
from flask_restful.reqparse import RequestParser

from app import db
from app.models.user import UserModel
from app.models.revoked_token import RevokedTokenModel


def to_identity(username):
    return {
        'username': username,
        'time': datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    }


class UserRegistration(Resource):
    def is_valid_post(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            parser = RequestParser()
            parser.add_argument('username', help = 'This field cannot be blank', required = True)
            parser.add_argument('password', help = 'This field cannot be blank', required = True)
            parser.add_argument('icon_url', help = 'This field cannot be blank', required = True)

            g.data = data = parser.parse_args()

            if UserModel.find_by_username(data['username']):
                return {
                    'message': 'User {} already exists'. format(data['username'])
                }, 401
            return fn(*args, **kwargs)
        return wrapped

    @is_valid_post
    def post(self):
        data = g.data

        new_user = UserModel(
            username = data['username'],
            password = UserModel.generate_hash(data['password']),
            icon_url = data['icon_url'])

        try:
            new_user.save_to_db()
            access_token = create_access_token(identity = to_identity(data['username']))
            refresh_token = create_refresh_token(identity = to_identity(data['username']))
            return {
                'message': 'User {} was created'.format(data['username']),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        except:
            db.session.rollback()
            return {
                'message': 'Registration went wrong'
            }, 500


class UserLogin(Resource):
    def is_valid_post(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            parser = RequestParser()
            parser.add_argument('username', help = 'This field cannot be blank', required = True)
            parser.add_argument('password', help = 'This field cannot be blank', required = True)

            g.data = data = parser.parse_args()
            g.current_user = current_user = UserModel.find_by_username(data['username'])

            if not current_user:
                return {
                    'message': 'Wrong credentials'
                }, 401
            return fn(*args, **kwargs)
        return wrapped

    @is_valid_post
    def post(self):
        data = g.data
        current_user = g.current_user

        if UserModel.verify_hash(data['password'], current_user.password):
            access_token = create_access_token(identity = to_identity(data['username']))
            refresh_token = create_refresh_token(identity = to_identity(data['username']))
            return {
                'message': 'Logged in as {}'.format(current_user.username),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        else:
            return {
                'message': 'Wrong credentials'
            }, 401


class UserLogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']

        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {
                'message': 'Access token has been revoked'
            }
        except:
            db.session.rollback()
            return {
                'message': 'Logout access went wrong'
            }, 500


class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']

        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {
                'message': 'Refresh token has been revoked'
            }
        except:
            db.session.rollback()
            return {
                'message': 'Logout refresh went wrong'
            }, 500


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity = to_identity(current_user))
        return {
            'access_token': access_token
        }
