import itertools

from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, reqparse
from flask_restful.reqparse import RequestParser

from app.models.user import UserModel
from app.models.group import GroupModel
from app.models.event import EventModel
from app.models.event import PictureModel
from app.models.subscription import SubscriptionModel

flatten = itertools.chain.from_iterable


class EventListResource(Resource):
    @jwt_required
    def get(self):
        username = get_jwt_identity()
        current_user = UserModel.find_by_username(username)

        if not current_user:
            return {
                'message': 'User {} does not exist'.format(username)
            }

        events = flatten(list(map(
            lambda x: x.events,
            current_user.groups)))

        return list(map(
            lambda x: x.to_json(with_group=True, multi_pics=False),
            events))

    @jwt_required
    def post(self):
        parser = RequestParser()
        parser.add_argument('name',
            help='This field cannot be blank',
            required=True)
        parser.add_argument('added_date',
            help='This field cannot be blank',
            required=True)
        parser.add_argument('group',
            type=dict,
            location='json',
            help='This field cannot be blank',
            required=True)
        parser.add_argument('pictures',
            type=list,
            location='json',
            help='This field cannot be blank',
            required=True)

        data = parser.parse_args()

        # check if group json or pictures list are empty
        if not data['group'] or 'id' not in data['group'] or not data['pictures']:
            return {
                'message': 'group should not be empty hash. pictures should contain urls'
            }

        # check if current_user has access to the group
        username = get_jwt_identity()
        group = GroupModel.query.join(GroupModel.users).filter(
            UserModel.username == username,
            GroupModel.id == data['group']['id']).first()

        if not group:
            return {
                'message': 'Group id {} does not exist'.format(data['group']['id'])
            }

        new_event = EventModel(
            name=data['name'],
            added_date=data['added_date'],
            group_id=data['group']['id']
        )
        for url in data['pictures']:
            pic = PictureModel(url=url)
            new_event.pictures.append(pic)

        try:
            new_event.save_to_db()
            return {
                'message': 'Event has been created'
            }
        except:
            return {
                'message': 'Something went wrong'
            }, 500


class EventResource(Resource):
    @jwt_required
    def get(self, id):
        username = get_jwt_identity()
        current_user = UserModel.find_by_username(username)

        if not current_user:
            return {
                'message': 'User {} does not exist'.format(username)
            }

        event = EventModel.query.get(id)

        if not event:
            return {
                'message': 'Event id {} does not exist'.format(id)
            }

        user = list(filter(lambda x: x.id == current_user.id, event.group.users))

        if not user:
            return {
                'message': 'Event id {} does not exist'.format(id)
            }

        res = event.to_json(with_group=True, multi_pics=True, with_sub=current_user.id)
        return res


class PictureListResource(Resource):
    @jwt_required
    def post(self, event_id):
        parser = RequestParser()
        parser.add_argument('pictures',
            type=list,
            location='json',
            help='This field cannot be blank',
            required=True)

        data = parser.parse_args()

        # check if group json or pictures list are empty
        if not data['pictures']:
            return {
                'message': 'pictures field should not be empty'
            }

        event = EventModel.query.get(event_id)

        if not event:
            return {
                'message': 'Event id {} does not exist'.format(event_id)
            }

        # check if current_user has access to the group
        username = get_jwt_identity()
        group_id = event.group.id
        group = GroupModel.query.join(GroupModel.users).filter(
            UserModel.username == username,
            GroupModel.id == group_id).first()

        if not group:
            return {
                'message': 'Group id {} does not exist'.format(group_id)
            }

        for url in data['pictures']:
            pic = PictureModel(url=url)
            event.pictures.append(pic)

        try:
            event.save_to_db()
            return {
                'message': 'Pictures has been registered'
            }
        except:
            return {
                'message': 'Something went wrong'
            }, 500


class SubscriptionResource(Resource):
    @jwt_required
    def post(self, event_id):
        parser = RequestParser()
        parser.add_argument('class',
            location='json',
            help='This field cannot be blank',
            required=True)

        data = parser.parse_args()

        # check if class is correct type
        if data['class'] not in ["people", "landscape", "people/landscape"]:
            return {
                'message': 'class field should not be empty'
            }

        event = EventModel.query.get(event_id)

        # check if event exists
        if not event:
            return {
                'message': 'Event id {} does not exist'.format(event_id)
            }

        # check if current_user has access to the group
        username = get_jwt_identity()
        group_id = event.group.id
        group = GroupModel.query.join(GroupModel.users).filter(
            UserModel.username == username,
            GroupModel.id == group_id).first()

        if not group:
            return {
                'message': 'Group id {} does not exist'.format(group_id)
            }

        current_user = UserModel.find_by_username(username)
        sub = SubscriptionModel.query.filter_by(user_id=current_user.id, event_id=event_id).first()

        if not sub:
            sub = SubscriptionModel(
                user_id=current_user.id,
                event_id=event_id,
                klass=data['class'])
        else:
            sub.klass = data['class']

        try:
            sub.save_to_db()
            return {
                'message': 'Subscription has been created'
            }
        except:
            return {
                'message': 'Something went wrong'
            }, 500

