import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_ENV', 'development') == 'development'
    PORT = int(os.getenv('PORT', 5001))
    HOST = os.getenv('HOST', '0.0.0.0')
    
    # Database settings
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'verification_system.db')
    
    # Upload settings
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov'}
    
    # Face recognition settings
    FACE_MODEL = 'VGG-Face'  # Best CPU performance as per research paper
    FACE_DETECTOR = 'opencv'
    FACE_SIMILARITY_THRESHOLD = 0.4  # VGGFace cosine distance threshold
    
    # License OCR settings
    OCR_LANGUAGES = ['en']
    OCR_GPU = False  # CPU mode for free deployment
    
    # Liveness detection settings
    LIVENESS_ENABLED = True
    LIVENESS_BLINK_THRESHOLD = 2
    EYE_AR_THRESHOLD = 0.22
    EYE_AR_CONSEC_FRAMES = 3
    
    # Verification thresholds
    LICENSE_MATCH_THRESHOLD = 0.6  # 60% match required
    
    @staticmethod
    def init_app():
        """Initialize application directories"""
        Path(Config.UPLOAD_FOLDER).mkdir(exist_ok=True)
        print(f"✅ Upload folder created: {Config.UPLOAD_FOLDER}")
