from src.routes.user import auth_bp
from src.routes.room import rooms_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(rooms_bp)