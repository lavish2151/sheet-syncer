from flask import Flask
from app.sync.routes import sync_bp
from app.extensions import db, migrate
from app.models import *
from app.scheduler import start_scheduler   
from dotenv import load_dotenv
import os
from app.ai_routes import ai_bp
import logging

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_PATH")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    migrate.init_app(app, db)
    app.register_blueprint(sync_bp)
    app.register_blueprint(ai_bp)
    # start_scheduler(app)
    logging.basicConfig(
    level=logging.INFO,  # Show INFO and above level logs
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')

    return app
