from src.routes.login import login_bp
from src.routes.room import rooms_bp

def register_blueprints(app):
    app.register_blueprint(login_bp)
    app.register_blueprint(rooms_bp)
