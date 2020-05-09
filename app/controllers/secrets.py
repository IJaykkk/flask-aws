import time
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource

class SecretResource(Resource):
    @jwt_required
    def get(self):
        return {
            'answer': get_jwt_identity()
        }
