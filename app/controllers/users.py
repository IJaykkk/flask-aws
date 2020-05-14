from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from app.models.user import UserModel


class UserListResource(Resource):
    @jwt_required
    def get(self):
        return UserModel.return_all()


class UserResource(Resource):
    @jwt_required
    def get(self):
        username = get_jwt_identity()
        current_user = UserModel.find_by_username(username)
        if not current_user:
            return {
                'message': 'Wrong access token'
            }, 401
        else:
            return {
                'id': current_user.id,
                'username': current_user.username
            }
