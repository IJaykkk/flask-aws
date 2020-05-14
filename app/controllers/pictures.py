import os
from threading import Thread
from functools import wraps

from flask import g, request
from flask_jwt_extended import (create_refresh_token, jwt_required)
from flask_restful import Resource, reqparse
from flask_restful.reqparse import RequestParser

from app import db
from app.models.picture import PictureModel
from app.models.event import EventModel


class MQTT(Thread):
    def __init__(self, klasses, event_id, event_name):
        Thread.__init__(self)
        self.klasses = klasses
        self.event_id = event_id
        self.event_name = event_name

    def run(self):
        print('Start: Send MQTT to broker...')

        for klass in set(self.klasses.values()):
            cmd = "mqtt pub -t '{}/{}' -h '{}' -p '{}' -m 'Someone uploaded photos of {} in {} event'  -C 'wss' -u '{}' -P '{}'".format(
                self.event_id, klass,
                os.environ['BROKER_HOST'], os.environ['BROKER_PORT'],
                klass, self.event_name,
                os.environ['BROKER_USER'], os.environ['BROKER_PASSWORD'])
            os.system(cmd)

        print('End: Send MQTT to broker...')


class PictureBestshotResource(Resource):
    def is_valid_post(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            parser = RequestParser()
            parser.add_argument('event_id',
                type=str,
                location='json',
                help='This field cannot be blank',
                required=True)
            parser.add_argument('bestshots',
                type=list,
                location='json',
                help='This field cannot be blank',
                required=True)

            g.data = data = parser.parse_args()
            json = request.json

            # check event_id
            if not data['event_id'].isdigit():
                return {
                    'message': 'event_id field should be int'
                }, 400

            # check if group json or bestshots list are empty
            if not json['bestshots'] \
                or not isinstance(json['bestshots'], list) \
                or any(map(lambda x: not isinstance(x, str), json['bestshots'])):

                return {
                    'message': 'bestshots field should not be empty and its elements are str'
                }, 400

            # check if event exists
            event_id = int(data['event_id'])
            event = EventModel.query.get(event_id)
            if not event:
                return {
                    'message': 'Event id {} does not exist'.format(event_id)
                }, 404

            return fn(*args, **kwargs)
        return wrapped

    @jwt_required
    @is_valid_post
    def post(self):
        data = g.data

        try:
            pictures = PictureModel.query.filter(
                PictureModel.event_id == data['event_id'],
                PictureModel.url.in_(data['bestshots'])).all()
            for picture in pictures:
                picture.is_bestshot = True
                db.session.add(picture)
            db.session.commit()
            return {
                'message': 'Bestshots have been recorded'
            }
        except:
            db.session.rollback()
            return {
                'message': 'Something went wrong'
            }, 500


class PictureClassResource(Resource):
    def is_valid_post(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            parser = RequestParser()
            parser.add_argument('event_id',
                location='json',
                help='This field cannot be blank',
                required=True)
            parser.add_argument('classes',
                type=dict,
                location='json',
                help='This field cannot be blank',
                required=True)

            g.data = data = parser.parse_args()
            json = request.json

            # check if classes is dict
            if not json['classes'] or not isinstance(json['classes'], dict):
                return {
                    'message': 'classes field should not be empty'
                }, 400

            # check if event exists
            event_id = int(data['event_id'])
            g.event = event = EventModel.query.get(event_id)
            if not event:
                return {
                    'message': 'Event id {} does not exist'.format(event_id)
                }, 404

            return fn(*args, **kwargs)
        return wrapped

    @jwt_required
    @is_valid_post
    def post(self):
        data = g.data
        event = g.event

        try:
            pictures = PictureModel.query.filter(
                PictureModel.event_id == data['event_id'],
                PictureModel.url.in_(data['classes'].keys())).all()

            for picture in pictures:
                picture.klass = data['classes'][picture.url]
                db.session.add(picture)
            db.session.commit()

            # mqtt send
            thread = MQTT(data['classes'], event.id, event.name)
            thread.start()

            return {
                'message': 'Picture class has been registered'
            }
        except:
            db.session.rollback()
            return {
                'message': 'Something went wrong'
            }, 500
