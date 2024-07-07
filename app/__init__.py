from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import config  # Ensure this line imports the config correctly
from flask_cors import CORS

db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_name):
    app = Flask(__name__)

    # Load configuration from the config object
    app.config.from_object(config[config_name])

    # Enable Cross-Origin Resource Sharing (CORS) for the app
    CORS(app)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)

    # Register Blueprints
    from .views import auth_bp, user_bp, org_bp, user_home_bp  # Ensure these imports are correct
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(org_bp)
    app.register_blueprint(user_home_bp)

    return app