from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, reqparse
from flask_restful.reqparse import RequestParser

from app.models.user import UserModel
from app.models.group import GroupModel


class GroupListResource(Resource):
    @jwt_required
    def get(self):
        username = get_jwt_identity()
        current_user = UserModel.find_by_username(username)

        if not current_user:
            return {
                'message': 'User {} does not exist'.format(username)
            }

        return list(map(lambda x: x.to_json(with_user=True), current_user.groups))

    @jwt_required
    def post(self):
        parser = RequestParser()
        parser.add_argument('name',
            help='This field cannot be blank',
            required=True)
        parser.add_argument('user_ids',
            type=list,
            location='json',
            help='This field cannot be blank')

        data = parser.parse_args()

        # Only check if user_ids list is empty
        if not data['user_ids'] or isinstance(data['user_ids'][0], str):
            return {
                'message': 'user_ids must be not empty list and its element must be integer'
            }

        new_group = GroupModel(name=data['name'])
        users = UserModel.query.filter(UserModel.id.in_(data['user_ids']))
        for user in users:
            new_group.users.append(user)

        try:
            new_group.save_to_db()
            return {
                'message': 'Group has been created'
            }
        except:
            return {
                'message': 'Something went wrong'
            }, 500


class GroupResource(Resource):
    @jwt_required
    def get(self, id):
        username = get_jwt_identity()
        current_user = UserModel.find_by_username(username)

        if not current_user:
            return {
                'message': 'User {} does not exist'.format(username)
            }

        groups = list(filter(
            lambda x: x.id == id,
            current_user.groups
        ))

        if not groups:
            return {
                'message': 'Group id {} does not exist'.format(id)
            }

        group = groups[0]
        res = group.to_json(with_user=True)
        res.update({
            'events': list(map(
                lambda x: x.to_json(with_group=False, multi_pics=False),
                group.events))
        })

        return res
