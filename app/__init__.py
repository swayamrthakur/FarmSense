from flask import Flask
from flask_cors import CORS
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    from .routes import prediction_bp, health_bp
    app.register_blueprint(prediction_bp, url_prefix="/api")
    app.register_blueprint(health_bp, url_prefix="/api")

    from .routes.prediction import load_models
    load_models()

    return app