from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import logging
from logging.handlers import RotatingFileHandler
import os
from flask_talisman import Talisman

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Talisman(app, content_security_policy=None)
    
    db.init_app(app)
    
    with app.app_context():
        from . import routes
        db.create_all()
        
        # Create initial player if none exists
        from .models import Player
        if not Player.query.first():
            player = Player(name="Player 1")
            db.session.add(player)
            db.session.commit()
        
        if not app.debug:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/habit-quest.log', maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('Habit Quest startup')
        
        return app 