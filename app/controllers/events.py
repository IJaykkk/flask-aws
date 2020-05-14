import os
import itertools
import requests
from threading import Thread
from datetime import datetime
from functools import wraps

from flask import g, request
from flask_jwt_extended import (jwt_required, get_jwt_identity, create_access_token)
from flask_restful import Resource, reqparse
from flask_restful.reqparse import RequestParser

from app import db
from app.models.user import UserModel
from app.models.group import GroupModel
from app.models.event import EventModel
from app.models.event import PictureModel
from app.models.subscription import SubscriptionModel

flatten = itertools.chain.from_iterable

def to_identity(username):
    return {
        'username': username,
        'time': datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    }


class SendRequest(Thread):
    def __init__(self, partial_pics, all_pics, event_id, token):
        Thread.__init__(self)
        self.partial_pics = partial_pics
        self.all_pics = all_pics
        self.event_id = event_id
        self.token = token

    def run(self):
        print('Start: Send pics to ML...')

        headers = { 'Authorization': 'Bearer {}'.format(self.token) }

        # class
        json = {
            'event_id': str(self.event_id),
            'file_names': self.partial_pics
        }
        try:
            requests.post(os.environ['ML_CLASS_ENDPOINT'], json=json, headers=headers)
            print("request to {} succeeded".format(os.environ['ML_CLASS_ENDPOINT']))
        except:
            print("request to {} failed".format(os.environ['ML_CLASS_ENDPOINT']))

        # bestshosts
        json = {
            'event_id': str(self.event_id),
            'file_names': self.all_pics
        }
        try:
            requests.post(os.environ['ML_BEST_ENDPOINT'], json=json, headers=headers)
            print("request to {} succeeded".format(os.environ['ML_BEST_ENDPOINT']))
        except:
            print("request to {} failed".format(os.environ['ML_BEST_ENDPOINT']))

        print('End: Send pics to ML...')


class EventListResource(Resource):
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
        groups = GroupModel.query.with_parent(current_user).all()
        events = flatten(list(map(
            lambda x: x.events,
            groups)))
        return list(map(
            lambda x: x.to_json(with_group=True, multi_pics=False),
            events))

    def is_valid_post(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            parser = RequestParser()
            parser.add_argument('name',
                type=str,
                help='This field cannot be blank',
                required=True)
            parser.add_argument('added_date',
                type=str,
                help='This field cannot be blank',
                required=True)
            parser.add_argument('group',
                type=dict,
                location='json',
                help='This field cannot be blank',
                required=True)
            parser.add_argument('pictures',
                type=list,
                default=[],
                location='json',
                help='This field cannot be blank',
                required=True)

            g.data = data = parser.parse_args()
            json = request.json

            # check added_date is of correct format
            try:
                datetime.strptime(data['added_date'], "%m/%d/%Y")
            except:
                return {
                    'message': 'added_date should be of %m/%d/%Y format'
                }, 400

            # check if group has id
            if not json['group'] \
                or not isinstance(json['group'], dict) \
                or 'id' not in json['group'] \
                or not isinstance(data['group']['id'], int):

                return {
                    'message': 'group should not be empty hash. And, it needs to have id'
                }, 400

            if not json['pictures'] \
                or not isinstance(json['pictures'], list) \
                or any(map(lambda x: not isinstance(x, str), json['pictures'])):

                return {
                    'message': 'pictures should contain urls'
                }, 400

            # check if current_user has access to the group
            username = get_jwt_identity()
            try:
                g.group = group = GroupModel.query.join(GroupModel.users).filter(
                    UserModel.username == username,
                    GroupModel.id == data['group']['id']).first()
            except:
                group = None
                db.session.rollback()
            finally:
                if not group:
                    return {
                        'message': 'Group id {} does not exist'.format(data['group']['id'])
                    }, 404

            return fn(*args, **kwargs)
        return wrapped

    @jwt_required
    @is_valid_post
    def post(self):
        data = g.data
        group = g.group

        new_event = EventModel(
            name=data['name'],
            added_date=data['added_date'],
            group_id=group.id
        )
        for url in data['pictures']:
            pic = PictureModel(url=url)
            new_event.pictures.append(pic)

        try:
            new_event.save_to_db()

            # send request to machine learning
            username = get_jwt_identity()
            token = create_access_token(identity=to_identity(username))
            pics = list(map(lambda x: x.url, new_event.pictures))
            thread = SendRequest(pics, pics, new_event.id, token)
            thread.start()

            return {
                'id': new_event.id,
                'message': 'Event has been created'
            }
        except:
            db.session.rollback()
            return {
                'message': 'Something went wrong'
            }, 500


class EventResource(Resource):
    def is_valid_get(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            username = get_jwt_identity()

            g.current_user = current_user = UserModel.find_by_username(username)
            if not current_user:
                return {
                    'message': 'User {} does not exist'.format(username)
                }, 401

            # kwargs['event_id'] is always int, so we don't need try block
            g.event = event = EventModel.query.get(kwargs['event_id'])
            if not event:
                return {
                    'message': 'Event id {} does not exist'.format(kwargs['event_id'])
                }, 404

            # current user doesn't have access to the event
            user = list(filter(lambda x: x.id == current_user.id, event.group.users))
            if not user:
                return {
                    'message': 'Event id {} does not exist'.format(kwargs['event_id'])
                }, 404
            return fn(*args, **kwargs)
        return wrapped

    @jwt_required
    @is_valid_get
    def get(self, event_id):
        event = g.event
        current_user = g.current_user
        return event.to_json(with_group=True, multi_pics=True, with_sub=current_user.id)


class PictureListResource(Resource):
    def is_valid_post(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            parser = RequestParser()
            parser.add_argument('pictures',
                type=list,
                location='json',
                help='This field cannot be blank',
                required=True)

            g.data = data = parser.parse_args()
            json = request.json

            # check if pictures
            if not json['pictures'] \
                or not isinstance(json['pictures'], list) \
                or any(map(lambda x: not isinstance(x, str), json['pictures'])):

                return {
                    'message': 'pictures should contain urls'
                }, 400

            # kwargs['event_id'] is always int, so don't need try block
            g.event = event = EventModel.query.get(kwargs['event_id'])
            if not event:
                return {
                    'message': 'Event id {} does not exist'.format(kwargs['event_id'])
                }, 404

            # check if current_user has access to the group
            username = get_jwt_identity()
            group_id = event.group.id
            try:
                group = GroupModel.query.join(GroupModel.users).filter(
                    UserModel.username == username,
                    GroupModel.id == group_id).first()
            except:
                group = None
                db.session.rollback()
            finally:
                if not group:
                    return {
                        'message': 'Group id {} does not exist'.format(group_id)
                    }, 404
            return fn(*args, **kwargs)
        return wrapped

    @jwt_required
    @is_valid_post
    def post(self, event_id):
        data = g.data
        event = g.event

        for url in data['pictures']:
            pic = PictureModel(url=url)
            event.pictures.append(pic)

        try:
            event.save_to_db()

            # send request to machine learning
            username = get_jwt_identity()
            token = create_access_token(identity=to_identity(username))
            pics = list(map(lambda x: x.url, event.pictures))
            thread = SendRequest(data['pictures'], pics, event.id, token)
            thread.start()

            return {
                'message': 'Pictures has been registered'
            }
        except:
            db.session.rollback()
            return {
                'message': 'Something went wrong'
            }, 500


class SubscriptionResource(Resource):
    def is_valid_post(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            parser = RequestParser()
            parser.add_argument('class',
                type=str,
                help='This field cannot be blank',
                required=True)

            g.data = data = parser.parse_args()

            # check if class is correct type
            if data['class'] not in ['people', 'landscape']:
                return {
                    'message': 'class field should not be empty'
                }, 400

            # check if event exists
            g.event = event = EventModel.query.get(kwargs['event_id'])
            if not event:
                return {
                    'message': 'Event id {} does not exist'.format(kwargs['event_id'])
                }, 404

            # check if current_user has access to the group
            username = get_jwt_identity()
            g.current_user = current_user = UserModel.find_by_username(username)
            group = GroupModel.query.join(GroupModel.users).filter(
                UserModel.username == username,
                GroupModel.id == event.group.id).first()
            if not group:
                return {
                    'message': 'Group id {} does not exist'.format(kwargs['event_id'])
                }, 404

            return fn(*args, **kwargs)
        return wrapped

    @jwt_required
    @is_valid_post
    def post(self, event_id):
        data = g.data
        event = g.event
        current_user = g.current_user

        sub = SubscriptionModel.query.filter_by(user_id=current_user.id, event_id=event.id).first()
        if not sub:
            sub = SubscriptionModel(
                user_id=current_user.id,
                event_id=event.id,
                klass=data['class'])
        elif sub.klass != data['class']:
            sub.klass = 'people/landscape'

        try:
            sub.save_to_db()
            return {
                'message': 'Subscription has been created'
            }
        except:
            db.session.rollback()
            return {
                'message': 'Something went wrong'
            }, 500
