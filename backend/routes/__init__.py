# Routes package initialization
from flask import Blueprint

def register_routes(app):
    """Register all application routes"""
    from .registration import registration_bp
    from .verification import verification_bp
    
    app.register_blueprint(registration_bp, url_prefix='/api')
    app.register_blueprint(verification_bp, url_prefix='/api')
    
    
    print("✅ All routes registered")
