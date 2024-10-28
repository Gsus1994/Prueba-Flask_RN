#Backend/src/config.py

import os
import logging
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from flask_pymongo import PyMongo
from datetime import datetime, timedelta
from flask_jwt_extended import JWTManager
from cachelib.file import FileSystemCache
from logging.handlers import TimedRotatingFileHandler

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(base_dir, '.env'))

class Config:
    MONGO_URI = os.getenv('MONGO_URI')
    SECRET_KEY = os.getenv('SECRET_KEY', 'mysecretkey')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwtsecretkey')
    TOKEN_EXPIRATION = int(os.getenv('TOKEN_EXPIRATION', 5))
    AES_KEY = bytes.fromhex(os.getenv('AES_KEY'))

    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY', 'AWS_SECRET')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET', 'AWS_SECRET')
    AWS_REGION = os.getenv('AWS_REGION', 'AWS_REGION')
    AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET', 'AWS_S3_BUCKET')

    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True')
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'False')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')

    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    PASSWORD_RESET_CODE_EXPIRATION = int(os.getenv('PASSWORD_RESET_CODE_EXPIRATION', 900))

    # Configuración de la sesión en el sistema de archivos usando CacheLib
    SESSION_FILE_DIR = os.getenv('SESSION_FILE_DIR')
    if not os.path.isabs(SESSION_FILE_DIR):
        SESSION_FILE_DIR = os.path.join(base_dir, SESSION_FILE_DIR)

    # Verificar si el directorio de sesión existe, si no, crearlo
    if not os.path.exists(SESSION_FILE_DIR):
        os.makedirs(SESSION_FILE_DIR)

    SESSION_CACHE = FileSystemCache(SESSION_FILE_DIR, threshold=int(os.getenv('SESSION_FILE_THRESHOLD', 100)))
    SESSION_FILE_MODE = int(os.getenv('SESSION_FILE_MODE', 0o600), 8)

    # Configuración de la vida útil de los archivos de sesión (en horas)
    SESSION_LIFETIME_HOURS = int(os.getenv('SESSION_LIFETIME_HOURS', 24))
    PERMANENT_SESSION_LIFETIME = timedelta(hours=SESSION_LIFETIME_HOURS)

    # Configuración de logs
    LOG_DIR = os.getenv('LOG_DIR')
    if not os.path.isabs(LOG_DIR):
        LOG_DIR = os.path.join(base_dir, LOG_DIR)

    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    LOG_FILE = os.path.join(LOG_DIR, 'app.log')
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', 20 * 1024 * 1024))
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 10))
    LOG_LEVEL = getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper())

class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = logging.DEBUG

class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = logging.WARNING

config_by_name = dict(
    development=DevelopmentConfig,
    production=ProductionConfig
)

jwt = JWTManager()
mongo = PyMongo()
bcrypt = Bcrypt()

def ensure_directories_exist(app):
    session_dir = app.config['SESSION_FILE_DIR']
    if not os.path.exists(session_dir):
        os.makedirs(session_dir)
        app.logger.info(f"Directorio de sesiones creado en: {session_dir}")

    log_dir = os.path.dirname(app.config['LOG_FILE'])
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        app.logger.info(f"Directorio de logs creado en: {log_dir}")

def cleanup_sessions(app):
    now = datetime.now()
    session_lifetime = timedelta(hours=int(os.getenv('SESSION_LIFETIME_HOURS', 24)))
    session_dir = app.config['SESSION_FILE_DIR']

    if not os.path.exists(session_dir):
        app.logger.warning(f"Directorio de sesiones no encontrado: {session_dir}")
        return

    for session_file in os.listdir(session_dir):
        session_path = os.path.join(session_dir, session_file)
        if os.path.isfile(session_path):
            file_mtime = datetime.fromtimestamp(os.path.getmtime(session_path))
            if now - file_mtime > session_lifetime:
                try:
                    os.remove(session_path)
                    app.logger.info(f"Archivo de sesión eliminado: {session_file}")
                except Exception as e:
                    app.logger.error(f"Error eliminando el archivo {session_file}: {str(e)}")

def init_app(app):
    ensure_directories_exist(app)

    jwt.init_app(app)
    mongo.init_app(app)
    bcrypt.init_app(app)

    file_handler = TimedRotatingFileHandler(
        app.config['LOG_FILE'], 
        when='midnight',
        interval=1,  
        backupCount=app.config['LOG_BACKUP_COUNT'] 
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))
    file_handler.setLevel(app.config['LOG_LEVEL'])
    app.logger.addHandler(file_handler)
    app.logger.setLevel(app.config['LOG_LEVEL'])

    app.logger.info('App startup')

    cleanup_sessions(app)