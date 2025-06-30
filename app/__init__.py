from flask import Flask, jsonify
from flask_cors import CORS
from marshmallow import ValidationError

# Import extensions from the new central location
from .extensions import db, migrate, jwt
from config import config_by_name

def register_blueprints(app):
    """
    A helper function to register all blueprints.
    This is called from the factory to avoid circular imports.
    """
    # Import and register blueprints
    from .auth import auth_bp
    from .api.owners import owners_bp
    from .api.cars import cars_bp
    from .api.garages import garages_bp
    from .api.services import services_bp
    from .api.analytics import analytics_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(owners_bp, url_prefix='/api')
    app.register_blueprint(cars_bp, url_prefix='/api')
    app.register_blueprint(garages_bp, url_prefix='/api')
    app.register_blueprint(services_bp, url_prefix='/api')
    app.register_blueprint(analytics_bp, url_prefix='/api')


def create_app(config_name='development'):
    """
    Application factory function.
    Initializes the Flask app, extensions, and registers blueprints.
    """
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions with app context
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints after extensions are initialized
    register_blueprints(app)

    # Global error handler for Marshmallow validation errors
    @app.errorhandler(ValidationError)
    def handle_marshmallow_validation(err):
        return jsonify(err.messages), 400

    # JWT custom error messages
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"message": "Token has expired", "error": "token_expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"message": "Signature verification failed", "error": "invalid_token"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"message": "Request does not contain an access token", "error": "authorization_required"}), 401

    return app
