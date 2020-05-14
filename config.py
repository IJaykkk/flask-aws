import os
from datetime import timedelta
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = False
    SECRET_KEY = os.environ['SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=10800)
    BROKER_HOST=os.environ['BROKER_HOST']
    BROKER_PORT=os.environ['BROKER_PORT']
    BROKER_USER=os.environ['BROKER_USER']
    BROKER_PASSWORD=os.environ['BROKER_PASSWORD']
    ML_BEST_ENDPOINT=os.environ['ML_BEST_ENDPOINT']
    ML_CLASS_ENDPOINT=os.environ['ML_CLASS_ENDPOINT']
    #  SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    DEBUG = False


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
