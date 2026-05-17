"""
Configuration for Wedding Management System
Uses environment variables - no hardcoded credentials
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Secret key for session security - MUST set in production
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database configuration - XAMPP MySQL defaults
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),  # XAMPP default: empty
    'database': os.environ.get('DB_NAME', 'wedding_db'),
    'port': int(os.environ.get('DB_PORT', 3306)),
}

# Upload configuration
UPLOAD_FOLDER = BASE_DIR / 'static' / 'uploads'
VENDOR_UPLOAD_FOLDER = BASE_DIR / 'static' / 'uploads' / 'vendors'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Session configuration
SESSION_PERMANENT = False
PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
