# Firebase Authentication Service for Trivanta Edge ERP
# Handles user authentication and authorization

import firebase_admin
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials
from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import jwt
from utils.security import security_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FirebaseAuthService:
    """Firebase authentication service"""
    
    def __init__(self):
        self.initialized = False
        self.jwt_secret = "trivanta_erp_jwt_secret_2024"
        
    def initialize(self):
        """Initialize Firebase Auth service"""
        try:
            if not firebase_admin._apps:
                # Initialize Firebase Admin SDK
                cred = credentials.ApplicationDefault()
                firebase_admin.initialize_app(cred)
            
            self.initialized = True
            logger.info("Firebase Auth service initialized successfully")
            
        except Exception as e:
            logger.error(f"Firebase Auth initialization failed: {e}")
            self.initialized = False
    
    def is_ready(self) -> bool:
        """Check if Firebase Auth is ready"""
        return self.initialized
    
    def create_user(self, user_data: Dict[str, Any]) -> Optional[str]:
        """Create a new user in Firebase Auth"""
        if not self.is_ready():
            self.initialize()
        
        try:
            # Create user in Firebase Auth
            user_properties = {
                'email': user_data['email'],
                'password': user_data['password'],
                'display_name': user_data['name'],
                'email_verified': False,
                'disabled': False
            }
            
            # Add custom claims for role
            custom_claims = {
                'role': user_data.get('role', 'employee'),
                'department': user_data.get('department', 'General'),
                'erp_user_id': user_data.get('id', '')
            }
            
            user_record = firebase_auth.create_user(**user_properties)
            
            # Set custom claims
            firebase_auth.set_custom_user_claims(user_record.uid, custom_claims)
            
            logger.info(f"Firebase user created: {user_record.uid}")
            return user_record.uid
            
        except Exception as e:
            logger.error(f"Error creating Firebase user: {e}")
            return None
    
    def update_user(self, uid: str, user_data: Dict[str, Any]) -> bool:
        """Update user in Firebase Auth"""
        if not self.is_ready():
            self.initialize()
        
        try:
            update_data = {}
            
            if 'name' in user_data:
                update_data['display_name'] = user_data['name']
            
            if 'email' in user_data:
                update_data['email'] = user_data['email']
            
            if 'password' in user_data:
                update_data['password'] = user_data['password']
            
            if 'disabled' in user_data:
                update_data['disabled'] = user_data['disabled']
            
            # Update custom claims if role or department changed
            if 'role' in user_data or 'department' in user_data:
                current_claims = firebase_auth.get_user(uid).custom_claims or {}
                new_claims = {
                    **current_claims,
                    'role': user_data.get('role', current_claims.get('role', 'employee')),
                    'department': user_data.get('department', current_claims.get('department', 'General'))
                }
                firebase_auth.set_custom_user_claims(uid, new_claims)
            
            if update_data:
                firebase_auth.update_user(uid, **update_data)
            
            logger.info(f"Firebase user updated: {uid}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating Firebase user: {e}")
            return False
    
    def delete_user(self, uid: str) -> bool:
        """Delete user from Firebase Auth"""
        if not self.is_ready():
            self.initialize()
        
        try:
            firebase_auth.delete_user(uid)
            logger.info(f"Firebase user deleted: {uid}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting Firebase user: {e}")
            return False
    
    def get_user(self, uid: str) -> Optional[Dict[str, Any]]:
        """Get user from Firebase Auth"""
        if not self.is_ready():
            self.initialize()
        
        try:
            user_record = firebase_auth.get_user(uid)
            
            user_data = {
                'uid': user_record.uid,
                'email': user_record.email,
                'name': user_record.display_name,
                'email_verified': user_record.email_verified,
                'disabled': user_record.disabled,
                'created_at': user_record.user_metadata.creation_timestamp,
                'last_sign_in': user_record.user_metadata.last_sign_in_timestamp,
                'custom_claims': user_record.custom_claims or {}
            }
            
            return user_data
            
        except Exception as e:
            logger.error(f"Error getting Firebase user: {e}")
            return None
    
    def verify_id_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """Verify Firebase ID token"""
        if not self.is_ready():
            self.initialize()
        
        try:
            decoded_token = firebase_auth.verify_id_token(id_token)
            
            # Extract user information
            user_info = {
                'uid': decoded_token['uid'],
                'email': decoded_token.get('email', ''),
                'email_verified': decoded_token.get('email_verified', False),
                'role': decoded_token.get('role', 'employee'),
                'department': decoded_token.get('department', 'General'),
                'erp_user_id': decoded_token.get('erp_user_id', ''),
                'iat': decoded_token.get('iat', 0),
                'exp': decoded_token.get('exp', 0)
            }
            
            return user_info
            
        except Exception as e:
            logger.error(f"Error verifying ID token: {e}")
            return None
    
    def create_custom_token(self, uid: str, additional_claims: Dict[str, Any] = None) -> Optional[str]:
        """Create custom token for user"""
        if not self.is_ready():
            self.initialize()
        
        try:
            claims = additional_claims or {}
            custom_token = firebase_auth.create_custom_token(uid, claims)
            
            logger.info(f"Custom token created for user: {uid}")
            return custom_token.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Error creating custom token: {e}")
            return None
    
    def revoke_refresh_tokens(self, uid: str) -> bool:
        """Revoke refresh tokens for user"""
        if not self.is_ready():
            self.initialize()
        
        try:
            firebase_auth.revoke_refresh_tokens(uid)
            logger.info(f"Refresh tokens revoked for user: {uid}")
            return True
            
        except Exception as e:
            logger.error(f"Error revoking refresh tokens: {e}")
            return False
    
    def list_users(self, max_results: int = 1000) -> list:
        """List all users in Firebase Auth"""
        if not self.is_ready():
            self.initialize()
        
        try:
            users = []
            page = firebase_auth.list_users(max_results=max_results)
            
            for user in page.users:
                user_data = {
                    'uid': user.uid,
                    'email': user.email,
                    'name': user.display_name,
                    'email_verified': user.email_verified,
                    'disabled': user.disabled,
                    'created_at': user.user_metadata.creation_timestamp,
                    'last_sign_in': user.user_metadata.last_sign_in_timestamp,
                    'custom_claims': user.custom_claims or {}
                }
                users.append(user_data)
            
            logger.info(f"Listed {len(users)} Firebase users")
            return users
            
        except Exception as e:
            logger.error(f"Error listing Firebase users: {e}")
            return []
    
    def generate_jwt_token(self, user_data: Dict[str, Any], expires_in: int = 3600) -> str:
        """Generate JWT token for user"""
        try:
            payload = {
                'user_id': user_data.get('id', ''),
                'email': user_data.get('email', ''),
                'role': user_data.get('role', 'employee'),
                'department': user_data.get('department', 'General'),
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(seconds=expires_in)
            }
            
            token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
            logger.info(f"JWT token generated for user: {user_data.get('email', '')}")
            return token
            
        except Exception as e:
            logger.error(f"Error generating JWT token: {e}")
            return ""
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            logger.info(f"JWT token verified for user: {payload.get('email', '')}")
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid JWT token: {e}")
            return None
        except Exception as e:
            logger.error(f"Error verifying JWT token: {e}")
            return None
    
    def send_password_reset_email(self, email: str) -> bool:
        """Send password reset email"""
        if not self.is_ready():
            self.initialize()
        
        try:
            # Generate password reset link
            reset_link = firebase_auth.generate_password_reset_link(email)
            
            # TODO: Send email with reset link
            logger.info(f"Password reset link generated for: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending password reset email: {e}")
            return False
    
    def verify_password_reset_code(self, oob_code: str) -> Optional[str]:
        """Verify password reset code"""
        if not self.is_ready():
            self.initialize()
        
        try:
            # Verify the password reset code
            email = firebase_auth.verify_password_reset_code(oob_code)
            logger.info(f"Password reset code verified for: {email}")
            return email
            
        except Exception as e:
            logger.error(f"Error verifying password reset code: {e}")
            return None
    
    def confirm_password_reset(self, oob_code: str, new_password: str) -> bool:
        """Confirm password reset"""
        if not self.is_ready():
            self.initialize()
        
        try:
            firebase_auth.confirm_password_reset(oob_code, new_password)
            logger.info("Password reset confirmed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error confirming password reset: {e}")
            return False

# Global Firebase Auth service instance
firebase_auth_service = FirebaseAuthService()

def get_firebase_auth_service() -> FirebaseAuthService:
    """Get global Firebase Auth service instance"""
    return firebase_auth_service
