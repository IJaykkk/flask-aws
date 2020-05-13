import os
from threading import Thread

from flask_jwt_extended import (create_refresh_token, jwt_refresh_token_required)
from flask_restful import Resource, reqparse
from flask_restful.reqparse import RequestParser

from app import db
from app.models.picture import PictureModel
from app.models.event import EventModel


class Compute(Thread):
    def __init__(self, klasses, event):
        Thread.__init__(self)
        self.klasses = klasses
        self.event = event

    def run(self):
        print('Start: Send MQTT to broker...')

        for klass in set(self.klasses.values()):
            cmd = "mqtt pub -t '{}/{}' -h '{}' -p '{}' -m 'Someone uploaded photos of {} in {} event'  -C 'wss' -u '{}' -P '{}'".format(
                self.event.id, klass, os.environ['BROKER_HOST'], os.environ['BROKER_PORT'],
                klass, self.event.name, os.environ['BROKER_USER'], os.environ['BROKER_PASSWORD'])
            os.system(cmd)

        print('End: Send MQTT to broker...')


class PictureBestshotResource(Resource):
    @jwt_refresh_token_required
    def post(self):
        parser = RequestParser()
        parser.add_argument('event_id',
            location='json',
            help='This field cannot be blank',
            required=True)
        parser.add_argument('bestshots',
            type=list,
            location='json',
            help='This field cannot be blank',
            required=True)

        data = parser.parse_args()

        # check if group json or bestshots list are empty
        if not data['bestshots']:
            return {
                'message': 'bestshots field should not be empty'
            }, 400

        event_id = int(data['event_id'])
        event = EventModel.query.get(event_id)

        # check if event exists
        if not event:
            return {
                'message': 'Event id {} does not exist'.format(event_id)
            }, 404

        pictures = PictureModel.query.filter(
            PictureModel.event_id == event_id,
            PictureModel.url.in_(data['bestshots'])).all()

        try:
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
    @jwt_refresh_token_required
    def post(self):
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

        data = parser.parse_args()

        # check if group json or bestshots list are empty
        if not data['classes']:
            return {
                'message': 'classes field should not be empty'
            }, 400

        event_id = int(data['event_id'])
        event = EventModel.query.get(event_id)

        # check if event exists
        if not event:
            return {
                'message': 'Event id {} does not exist'.format(event_id)
            }, 404

        pictures = PictureModel.query.filter(
            PictureModel.event_id == event_id,
            PictureModel.url.in_(data['classes'].keys())).all()

        try:
            for picture in pictures:
                picture.klass = data['classes'][picture.url]
                db.session.add(picture)
            db.session.commit()

            # mqtt send
            thread = Compute(data['classes'], event)
            thread.start()

            return {
                'message': 'Picture class has been registered'
            }
        except:
            db.session.rollback()
            return {
                'message': 'Something went wrong'
            }, 500
