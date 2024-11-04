import os
import errno
import logging
from flask_bcrypt import Bcrypt
from flask_pymongo import PyMongo
from datetime import datetime, timedelta
from flask_jwt_extended import JWTManager
from cachelib.file import FileSystemCache
from logging.handlers import TimedRotatingFileHandler

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class Config:
    MONGO_URI = os.getenv('MONGO_URI')
    SECRET_KEY = os.getenv('SECRET_KEY', 'mysecretkey')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwtsecretkey')
    TOKEN_EXPIRATION = int(os.getenv('TOKEN_EXPIRATION', 5))
    AES_KEY = bytes.fromhex(os.getenv('AES_KEY'))

    # Configuración de la sesión en el sistema de archivos usando CacheLib
    SESSION_FILE_DIR = os.getenv('SESSION_FILE_DIR', '/app/flask_session')

    # Verificar si el directorio de sesión existe, si no, crearlo
    try:
        os.makedirs(SESSION_FILE_DIR, exist_ok=True)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise  # Solo ignorar si el error es que el archivo ya existe

    SESSION_CACHE = FileSystemCache(SESSION_FILE_DIR, threshold=int(os.getenv('SESSION_FILE_THRESHOLD', 100)))
    SESSION_FILE_MODE = int(os.getenv('SESSION_FILE_MODE', 0o600), 8)

    # Configuración de la vida útil de los archivos de sesión (en horas)
    SESSION_LIFETIME_HOURS = int(os.getenv('SESSION_LIFETIME_HOURS', 2))
    PERMANENT_SESSION_LIFETIME = timedelta(hours=SESSION_LIFETIME_HOURS)

    # Configuración de logs
    LOG_DIR = os.getenv('LOG_DIR', '/app/logs')

    # Verificar si el directorio de logs existe, si no, crearlo
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise  # Solo ignorar si el error es que el archivo ya existe

    LOG_FILE = os.path.join(LOG_DIR, 'app.log')
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', 20 * 1024 * 1024))  # Tamaño máximo de un archivo de log (20MB)
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 10))  # Número máximo de archivos de respaldo
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

def cleanup_sessions(app):
    now = datetime.now()
    session_lifetime = timedelta(hours=int(os.getenv('SESSION_LIFETIME_HOURS', 24)))
    session_dir = os.getenv('SESSION_FILE_DIR', '/app/flask_session')

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
    jwt.init_app(app)
    mongo.init_app(app)
    bcrypt.init_app(app)

    # Configuración del manejador de logs con rotación diaria
    file_handler = TimedRotatingFileHandler(
        app.config['LOG_FILE'], 
        when='midnight',  # Rotación diaria a medianoche
        interval=1,  # Intervalo de rotación
        backupCount=app.config['LOG_BACKUP_COUNT']  # Número máximo de archivos de respaldo
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))
    file_handler.setLevel(app.config['LOG_LEVEL'])
    app.logger.addHandler(file_handler)
    app.logger.setLevel(app.config['LOG_LEVEL'])

    app.logger.info('App startup')

    # Llamar a la función de limpieza de sesiones
    cleanup_sessions(app)