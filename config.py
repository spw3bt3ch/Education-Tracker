"""
Configuration management for SMIED application.
This module handles loading and validating environment variables.
"""

import os
from dotenv import load_dotenv

def load_environment():
    """Load environment variables from .env file"""
    # Priority order: .env -> aiven_config.env (fallback)
    if os.path.exists('.env'):
        load_dotenv('.env')
        print("✅ Loaded configuration from .env file")
    elif os.path.exists('aiven_config.env'):
        load_dotenv('aiven_config.env')
        print("⚠️  Using fallback configuration from aiven_config.env")
        print("   Consider copying aiven_config.env to .env for better security")
    else:
        print("❌ No environment configuration file found!")
        print("   Please create a .env file using env.template as a guide")
        # Set some default values to prevent immediate crashes
        os.environ.setdefault('SECRET_KEY', 'default-secret-key-change-in-production')
        os.environ.setdefault('DATABASE_URL', 'sqlite:///smied.db')

def get_required_env(key, default=None):
    """Get a required environment variable, raise error if not found"""
    value = os.getenv(key, default)
    if value is None:
        raise ValueError(f"Required environment variable {key} is not set")
    return value

def get_optional_env(key, default=None):
    """Get an optional environment variable with fallback"""
    return os.getenv(key, default)

# Load environment variables when module is imported
load_environment()

# Ensure environment variables are loaded before Config class is used
if not os.getenv('SECRET_KEY'):
    print("⚠️  SECRET_KEY not found, setting default value")
    os.environ['SECRET_KEY'] = 'smied-secret-key-2024-production-change-this-in-production'

class Config:
    """Application configuration class"""
    
    # Flask Configuration
    SECRET_KEY = get_required_env('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = get_optional_env('DATABASE_URL', 'sqlite:///smied.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    DATABASE_TOTAL_CAPACITY_GB = int(get_optional_env('DATABASE_TOTAL_CAPACITY_GB', '1'))
    BASE_URL = get_optional_env('BASE_URL', 'http://127.0.0.1:5000')
    
    # Email Configuration
    MAIL_SERVER = get_optional_env('MAIL_SERVER')
    MAIL_PORT = int(get_optional_env('MAIL_PORT', '587'))
    MAIL_USE_TLS = get_optional_env('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = get_optional_env('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = get_optional_env('MAIL_USERNAME')
    MAIL_PASSWORD = get_optional_env('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = get_optional_env('MAIL_DEFAULT_SENDER')
    MAIL_MAX_EMAILS = int(get_optional_env('MAIL_MAX_EMAILS', '100'))
    MAIL_SUPPRESS_SEND = get_optional_env('MAIL_SUPPRESS_SEND', 'False').lower() == 'true'
    
    # Paystack Configuration
    PAYSTACK_PUBLIC_KEY = get_optional_env('PAYSTACK_PUBLIC_KEY')
    PAYSTACK_SECRET_KEY = get_optional_env('PAYSTACK_SECRET_KEY')
    PAYSTACK_WEBHOOK_SECRET = get_optional_env('PAYSTACK_WEBHOOK_SECRET')
    
    # Default User Passwords
    SUPER_ADMIN_PASSWORD = get_optional_env('SUPER_ADMIN_PASSWORD', 'superadmin123')
    ADMIN_PASSWORD = get_optional_env('ADMIN_PASSWORD', 'admin123')
    TEACHER_PASSWORD = get_optional_env('TEACHER_PASSWORD', 'teacher123')
    PARENT_PASSWORD = get_optional_env('PARENT_PASSWORD', 'parent123')
