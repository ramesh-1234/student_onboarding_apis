from flask import Flask
from config import Config
from app.extensions import db
from flask_migrate import Migrate

migrate = Migrate()  # Initialize Flask-Migrate


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints

    from app.routes.verify import verify_bp
    from app.routes.account_preferences import account_bp
    from app.routes.aadhaar_verification import verify_aadhaar_bp
    app.register_blueprint(verify_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(verify_aadhaar_bp)

    return app
