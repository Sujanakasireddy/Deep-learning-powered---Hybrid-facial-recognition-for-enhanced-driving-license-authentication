#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Hybrid Facial Recognition + Driver's License Verification System
Backend API Server
"""

import os
import sys
import platform
import traceback

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path

from config import Config
from database import init_database
from routes import register_routes




# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize configuration
Config.init_app()

# Initialize database
init_database()

# Register all routes
register_routes(app)

# ========== MAIN ROUTES ==========

@app.route('/', methods=['GET'])
def home():
    """API information endpoint"""
    return jsonify({
        "message": "Hybrid Facial Recognition + Driver's License Verification System",
        "version": "1.0.0",
        "status": "running",
        "database": "SQLite (Local)",
        "platform": platform.machine(),
        "models": {
            "face_recognition": "OpenCV Haar Cascades",
            "license_ocr": "EasyOCR",
            "liveness_detection": "dlib (optional)"
        },
        "endpoints": {
            "registration": [
                "POST /api/register - Register new user",
                "GET /api/users - List all users",
                "DELETE /api/users/<user_id> - Delete user"
            ],
            "verification": [
                "POST /api/verify - Verify user (face + license)",
                "POST /api/verify-liveness - Verify with liveness detection",
                "POST /api/test-face - Test face detection only",
                "POST /api/test-license - Test license OCR only",
                "POST /api/verify-face-only - Verify face only and get user data",
                "GET /api/logs - Get verification logs"
            ],
            "system": [
                "GET / - API information",
                "GET /health - Health check",
                "GET /stats - System statistics"
            ]
        }
    }), 200

@app.route('/api/users/<user_id>/face', methods=['GET'])
def get_user_face(user_id):
    """Serve the user's face image"""
    filename = f'{user_id}_face.jpg'
    face_path = os.path.join(Config.UPLOAD_FOLDER, filename)
    if os.path.exists(face_path):
        return send_from_directory(Config.UPLOAD_FOLDER, filename)
    else:
        return jsonify({"error": "Face image not found"}), 404

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    from database import get_all_users
    
    try:
        users = get_all_users()
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "registered_users": len(users),
            "upload_folder": Config.UPLOAD_FOLDER,
            "models_loaded": True
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

@app.route('/stats', methods=['GET'])
def system_stats():
    """Get system statistics"""
    try:
        from database import get_all_users, get_verification_logs
        
        users = get_all_users()
        logs = get_verification_logs(limit=100)
        
        # Calculate success rate
        if len(logs) > 0:
            successful = len([log for log in logs if log['verification_status'] == 'verified'])
            success_rate = (successful / len(logs)) * 100
        else:
            success_rate = 0
        
        return jsonify({
            "total_users": len(users),
            "total_verifications": len(logs),
            "success_rate": round(success_rate, 2),
            "database_size": os.path.getsize(Config.DATABASE_PATH) if os.path.exists(Config.DATABASE_PATH) else 0,
            "upload_folder_files": len(list(Path(Config.UPLOAD_FOLDER).glob('*')))
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "message": "The requested URL was not found on the server"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "message": str(error)
    }), 500

# ========== RUN APPLICATION ==========

if __name__ == '__main__':
    print("=" * 70)
    print(" HYBRID VERIFICATION SYSTEM - BACKEND SERVER")
    print("=" * 70)
    print(f"📁 Database: {Path(Config.DATABASE_PATH).absolute()}")
    print(f"📂 Uploads: {Path(Config.UPLOAD_FOLDER).absolute()}")
    print(f"🌐 Host: {Config.HOST}")
    print(f"🔌 Port: {Config.PORT}")
    print(f"🐛 Debug: {Config.DEBUG}")
    print(f"🖥️  Platform: {platform.system()} ({platform.machine()})")
    print("=" * 70)
    print()
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
