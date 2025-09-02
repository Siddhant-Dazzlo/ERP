import bcrypt
import jwt
import secrets
import qrcode
import base64
import io
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import pyotp
from flask import current_app, request
from functools import wraps

class SecurityManager:
    def __init__(self):
        self.salt_rounds = 12
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt(rounds=self.salt_rounds)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength according to security policy"""
        errors = []
        warnings = []
        
        if len(password) < current_app.config['PASSWORD_MIN_LENGTH']:
            errors.append(f"Password must be at least {current_app.config['PASSWORD_MIN_LENGTH']} characters long")
        
        if current_app.config['PASSWORD_REQUIRE_UPPERCASE'] and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if current_app.config['PASSWORD_REQUIRE_LOWERCASE'] and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if current_app.config['PASSWORD_REQUIRE_DIGITS'] and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one digit")
        
        if current_app.config['PASSWORD_REQUIRE_SPECIAL'] and not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            errors.append("Password must contain at least one special character")
        
        # Additional strength checks
        if len(password) < 12:
            warnings.append("Consider using a longer password for better security")
        
        if password.lower() in ['password', '123456', 'qwerty', 'admin']:
            errors.append("Password is too common")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def generate_totp_secret(self) -> str:
        """Generate a new TOTP secret for 2FA"""
        return pyotp.random_base32()
    
    def generate_totp_qr_code(self, secret: str, user_email: str) -> str:
        """Generate QR code for TOTP setup"""
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user_email,
            issuer_name=current_app.config['TOTP_ISSUER']
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def verify_totp(self, secret: str, token: str) -> bool:
        """Verify TOTP token"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token)
    
    def generate_jwt_token(self, user_id: str, role: str, expires_in: Optional[timedelta] = None) -> str:
        """Generate JWT token for API authentication"""
        if expires_in is None:
            expires_in = current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
        
        payload = {
            'user_id': user_id,
            'role': role,
            'exp': datetime.utcnow() + expires_in,
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        
        return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    
    def generate_refresh_token(self, user_id: str) -> str:
        """Generate refresh token"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + current_app.config['JWT_REFRESH_TOKEN_EXPIRES'],
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        
        return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def generate_api_key(self) -> str:
        """Generate API key for external integrations"""
        return secrets.token_urlsafe(32)
    
    def generate_session_token(self) -> str:
        """Generate secure session token"""
        return secrets.token_urlsafe(64)

# Security decorators
def require_2fa(f):
    """Decorator to require 2FA for sensitive operations"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.json.get('user_id') if request.is_json else request.form.get('user_id')
        totp_token = request.json.get('totp_token') if request.is_json else request.form.get('totp_token')
        
        if not totp_token:
            return {'error': '2FA token required'}, 401
        
        # Verify 2FA token (implementation depends on your user storage)
        # This is a placeholder - implement based on your user management
        return f(*args, **kwargs)
    return decorated_function

def rate_limit(max_requests: int, window: int = 60):
    """Simple rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # This is a placeholder - implement proper rate limiting
            # Consider using Flask-Limiter for production
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Initialize security manager
security_manager = SecurityManager()

