"""
AI Rate Limiter Application Factory
"""
import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from celery import Celery

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
celery = Celery()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('app.config.config.Config')
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # Initialize Celery
    celery.conf.update(app.config)
    
    # Register blueprints
    from app.routes.queue_routes import queue_bp
    from app.routes.provider_routes import provider_bp
    from app.routes.worker_routes import worker_bp
    from app.routes.message_routes import message_bp

    app.register_blueprint(queue_bp, url_prefix='/api/v1')
    app.register_blueprint(provider_bp, url_prefix='/api/v1')
    app.register_blueprint(worker_bp, url_prefix='/api/v1')
    app.register_blueprint(message_bp, url_prefix='/api/v1')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'ai-rate-limiter',
            'version': '1.0.0'
        })
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app 