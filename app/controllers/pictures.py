from flask_jwt_extended import (create_refresh_token, jwt_refresh_token_required)
from flask_restful import Resource, reqparse
from flask_restful.reqparse import RequestParser

from app import db
from app.models.event import PictureModel


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
            }

        pictures = PictureModel.query.filter(
            PictureModel.event_id == int(data['event_id']),
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
            }

        pictures = PictureModel.query.filter(
            PictureModel.event_id == int(data['event_id']),
            PictureModel.url.in_(data['classes'].keys())).all()

        try:
            for picture in pictures:
                picture.klass = data['classes'][picture.url]
                db.session.add(picture)
            db.session.commit()
            return {
                'message': 'Picture class has been registered'
            }
        except:
            db.session.rollback()
            return {
                'message': 'Something went wrong'
            }, 500
