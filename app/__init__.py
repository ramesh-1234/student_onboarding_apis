import os
from flask import Flask, send_from_directory
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
    from app.routes.live_capture import live_capture_bp
    from app.routes.address_upload import address_upload_bp
    from app.routes.esignature import esignature_bp
    from app.routes.combined import combined_bp
    from app.routes.frontend import frontend_bp
    app.register_blueprint(verify_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(
        verify_aadhaar_bp)
    app.register_blueprint(live_capture_bp, url_prefix='/live-capture')
    app.register_blueprint(address_upload_bp)
    app.register_blueprint(esignature_bp, url_prefix='/esignature')
    app.register_blueprint(combined_bp, url_prefix='/combined')
    app.register_blueprint(frontend_bp)

    # Serve files from the uploads folder

    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        uploads_path = os.path.join(os.getcwd(), 'uploads')
        return send_from_directory(uploads_path, filename)
    return app
