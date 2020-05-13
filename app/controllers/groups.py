from functools import wraps

from flask import g, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, reqparse
from flask_restful.reqparse import RequestParser

from app import db
from app.models.user import UserModel
from app.models.group import GroupModel


class GroupListResource(Resource):
    def is_valid_get(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            username = get_jwt_identity()

            g.current_user = current_user = UserModel.find_by_username(username)
            if not current_user:
                return {
                    'message': 'User {} does not exist'.format(username)
                }, 401

            return fn(*args, **kwargs)
        return wrapped

    @jwt_required
    @is_valid_get
    def get(self):
        current_user = g.current_user
        return list(map(lambda x: x.to_json(with_user=True), current_user.groups))

    def is_valid_post(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            parser = RequestParser()
            parser.add_argument('name',
                type=str,
                help='This field cannot be blank',
                required=True)
            parser.add_argument('user_ids',
                type=list,
                location='json',
                help='This field cannot be blank')

            g.data = data = parser.parse_args()

            # check if user_ids list is empty and its content
            json = request.json
            if not json['user_ids'] \
                or not isinstance(json['user_ids'], list) \
                or any(map(lambda x: not isinstance(x, int), json['user_ids'])):
                return {
                    'message': 'user_ids must be not empty list and its element must be integer'
                }, 400

            return fn(*args, **kwargs)
        return wrapped

    @jwt_required
    @is_valid_post
    def post(self):
        data = g.data
        new_group = GroupModel(name=data['name'])

        try:
            users = UserModel.query.filter(UserModel.id.in_(data['user_ids'])).all()
            for user in users:
                new_group.users.append(user)
            new_group.save_to_db()
            return {
                'message': 'Group has been created'
            }
        except:
            db.session.rollback()
            return {
                'message': 'Something went wrong'
            }, 500


class GroupResource(Resource):
    def is_valid_get(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            username = get_jwt_identity()


            current_user = UserModel.find_by_username(username)
            if not current_user:
                return {
                    'message': 'User {} does not exist'.format(username)
                }, 401

            # kwargs['group_id' is always int, so we don't need try and except block
            g.group = group = GroupModel.query.join(GroupModel.users).filter(
                UserModel.username == username,
                GroupModel.id == kwargs['group_id']).first()
            if not group:
                return {
                    'message': 'Group id {} does not exist'.format(kwargs['group_id'])
                }, 404

            return fn(*args, **kwargs)
        return wrapped

    @jwt_required
    @is_valid_get
    def get(self, group_id):
        group = g.group

        res = group.to_json(with_user=True)
        res.update({
            'events': list(map(
                lambda x: x.to_json(with_group=False, multi_pics=False),
                group.events))
        })

        return res
