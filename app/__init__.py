from flask import Flask
from app.sync.routes import sync_bp
from app.extensions import db, migrate
from app.models import *
from app.scheduler import start_scheduler   
from dotenv import load_dotenv
import os

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_PATH")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    migrate.init_app(app, db)
    app.register_blueprint(sync_bp)
    start_scheduler(app)

    return app
