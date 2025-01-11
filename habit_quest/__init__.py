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
    
    # Add debug logging
    app.logger.info(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    db.init_app(app)
    Talisman(app, content_security_policy=None)
    
    with app.app_context():
        from . import routes
        
        # Create tables
        try:
            app.logger.info("Attempting to create database tables...")
            db.create_all()
            app.logger.info("Database tables created successfully")
            
            # Create initial player if none exists
            from .models import Player
            if not Player.query.count():
                player = Player(name="Player 1")
                db.session.add(player)
                db.session.commit()
                app.logger.info('Created initial player')
        except Exception as e:
            app.logger.error(f'Database initialization error: {str(e)}')
            # Re-raise the exception to see it in Render logs
            raise
        
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