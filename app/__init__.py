from flask import Flask
from app.sync.routes import sync_bp
from app.extensions import db, migrate
from app.models import *


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Lavish%40123456@localhost/employee_sync'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    migrate.init_app(app, db)
    app.register_blueprint(sync_bp)

    return app
