import os
from datetime import timedelta

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'trivanta_edge_erp_secret_key_2024_advanced'
    
    # Session Configuration
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    
    # Database Configuration (for future SQL implementation)
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///trivanta_erp.db'
    
    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'your-email@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'your-app-password'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@trivantaedge.com'
    
    # File Upload Configuration
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx'}
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt_secret_key_trivanta_2024'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Two-Factor Authentication
    TOTP_ISSUER = 'Trivanta Edge ERP'
    TOTP_ALGORITHM = 'sha1'
    TOTP_DIGITS = 6
    TOTP_PERIOD = 30
    
    # WebSocket Configuration
    SOCKETIO_MESSAGE_QUEUE = os.environ.get('SOCKETIO_MESSAGE_QUEUE') or 'redis://localhost:6379/0'
    
    # Analytics Configuration
    ANALYTICS_CACHE_DURATION = 300  # 5 minutes
    ANALYTICS_DATA_RETENTION_DAYS = 365
    
    # Security Configuration
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_DIGITS = True
    PASSWORD_REQUIRE_SPECIAL = True
    
    # API Configuration
    API_RATE_LIMIT = '100 per minute'
    API_VERSION = 'v1'
    
    # Notification Configuration
    NOTIFICATION_CHANNELS = ['email', 'websocket', 'sms']
    NOTIFICATION_RETRY_ATTEMPTS = 3
    
    # Backup Configuration
    BACKUP_ENABLED = True
    BACKUP_FREQUENCY_HOURS = 24
    BACKUP_RETENTION_DAYS = 30
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    
    # Production-specific settings
    MAIL_USE_TLS = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

