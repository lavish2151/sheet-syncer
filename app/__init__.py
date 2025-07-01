from flask import Flask
from app.sync.routes import sync_bp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(sync_bp)

    return app
