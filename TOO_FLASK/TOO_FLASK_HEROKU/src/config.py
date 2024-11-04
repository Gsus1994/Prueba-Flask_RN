# src/config.py

import os
import logging
from redis import Redis
from datetime import timedelta
from flask_bcrypt import Bcrypt
from flask_pymongo import PyMongo
from flask_session import Session 
from flask_jwt_extended import JWTManager

class Config:
    MONGO_URI = os.getenv('MONGO_URI')
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    TOKEN_EXPIRATION = int(os.getenv('TOKEN_EXPIRATION', 5))
    AES_KEY = bytes.fromhex(os.getenv('AES_KEY'))

    # Configuración de la sesión usando Redis
    SESSION_TYPE = 'redis'
    SESSION_REDIS = Redis.from_url(os.getenv('REDIS_URL'))
    SESSION_PERMANENT = False  # Ajusta según tus necesidades

    # Configuración de la vida útil de la sesión
    PERMANENT_SESSION_LIFETIME = timedelta(hours=int(os.getenv('SESSION_LIFETIME_HOURS', 4)))

    # Configuración del nivel de logs
    LOG_LEVEL = getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper())

class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = logging.DEBUG  # Nivel de log para desarrollo

class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = logging.WARNING  # Nivel de log para producción

config_by_name = dict(
    development=DevelopmentConfig,
    production=ProductionConfig
)

jwt = JWTManager()
mongo = PyMongo()
bcrypt = Bcrypt()
sess = Session()

def init_app(app):
    jwt.init_app(app)
    mongo.init_app(app)
    bcrypt.init_app(app)
    sess.init_app(app)

    # Configuración del manejador de logs para stdout
    import sys
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    stream_handler.setLevel(app.config['LOG_LEVEL'])
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(app.config['LOG_LEVEL'])

    app.logger.info('App startup')