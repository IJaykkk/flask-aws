from flask_jwt_extended import jwt_required
from flask_restful import Resource
from app.models.user import UserModel


class UserListResource(Resource):
    @jwt_required
    def get(self):
        return UserModel.return_all()

    @jwt_required
    def delete(self):
        return UserModel.delete_all()
