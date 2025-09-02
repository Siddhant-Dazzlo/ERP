from flask import request, jsonify
from functools import wraps
from datetime import datetime, timedelta
from utils.security import security_manager
from utils.data_manager import DataManager
from utils.email_service import email_service
from . import api_bp

data_manager = DataManager()

def require_api_auth(f):
    """Decorator to require API authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401
        
        token = auth_header.split(' ')[1]
        payload = security_manager.verify_jwt_token(token)
        
        if not payload or payload.get('type') != 'access':
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        request.user_id = payload.get('user_id')
        request.user_role = payload.get('role')
        
        return f(*args, **kwargs)
    return decorated_function

@api_bp.route('/auth/login', methods=['POST'])
def api_login():
    """API login endpoint"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    email = data['email']
    password = data['password']
    
    # Check for admin login
    if email == 'admin@trivantaedge.com' and password == 'admin123':
        access_token = security_manager.generate_jwt_token('admin_001', 'admin')
        refresh_token = security_manager.generate_refresh_token('admin_001')
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': 'admin_001',
                'name': 'System Administrator',
                'email': email,
                'role': 'admin'
            },
            'expires_in': 3600
        })
    
    # Check regular user credentials
    user = data_manager.authenticate_user(email, password)
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Check if 2FA is required
    if user.get('totp_secret'):
        return jsonify({
            'requires_2fa': True,
            'user_id': user['id'],
            'message': '2FA token required'
        }), 200
    
    # Generate tokens
    access_token = security_manager.generate_jwt_token(user['id'], user['role'])
    refresh_token = security_manager.generate_refresh_token(user['id'])
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role'],
            'department': user.get('department')
        },
        'expires_in': 3600
    })

@api_bp.route('/auth/2fa/verify', methods=['POST'])
def api_verify_2fa():
    """Verify 2FA token"""
    data = request.get_json()
    
    if not data or not data.get('user_id') or not data.get('totp_token'):
        return jsonify({'error': 'User ID and TOTP token required'}), 400
    
    user_id = data['user_id']
    totp_token = data['totp_token']
    
    user = data_manager.get_user_by_id(user_id)
    if not user or not user.get('totp_secret'):
        return jsonify({'error': 'Invalid user or 2FA not enabled'}), 400
    
    if not security_manager.verify_totp(user['totp_secret'], totp_token):
        return jsonify({'error': 'Invalid 2FA token'}), 401
    
    # Generate tokens
    access_token = security_manager.generate_jwt_token(user['id'], user['role'])
    refresh_token = security_manager.generate_refresh_token(user['id'])
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role'],
            'department': user.get('department')
        },
        'expires_in': 3600
    })

@api_bp.route('/auth/refresh', methods=['POST'])
def api_refresh_token():
    """Refresh access token"""
    data = request.get_json()
    
    if not data or not data.get('refresh_token'):
        return jsonify({'error': 'Refresh token required'}), 400
    
    refresh_token = data['refresh_token']
    payload = security_manager.verify_jwt_token(refresh_token)
    
    if not payload or payload.get('type') != 'refresh':
        return jsonify({'error': 'Invalid refresh token'}), 401
    
    user_id = payload.get('user_id')
    user = data_manager.get_user_by_id(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Generate new access token
    access_token = security_manager.generate_jwt_token(user['id'], user['role'])
    
    return jsonify({
        'access_token': access_token,
        'expires_in': 3600
    })

@api_bp.route('/auth/logout', methods=['POST'])
@require_api_auth
def api_logout():
    """Logout and invalidate tokens"""
    # In a real implementation, you would blacklist the token
    return jsonify({'message': 'Logged out successfully'})

@api_bp.route('/auth/2fa/setup', methods=['POST'])
@require_api_auth
def api_setup_2fa():
    """Setup 2FA for user"""
    user = data_manager.get_user_by_id(request.user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user.get('totp_secret'):
        return jsonify({'error': '2FA already enabled'}), 400
    
    # Generate new TOTP secret
    totp_secret = security_manager.generate_totp_secret()
    qr_code = security_manager.generate_totp_qr_code(totp_secret, user['email'])
    
    # Store secret temporarily (user needs to verify before saving)
    # In production, store this securely
    user['temp_totp_secret'] = totp_secret
    data_manager.save_data()
    
    return jsonify({
        'totp_secret': totp_secret,
        'qr_code': qr_code,
        'message': 'Scan QR code with authenticator app and verify with token'
    })

@api_bp.route('/auth/2fa/enable', methods=['POST'])
@require_api_auth
def api_enable_2fa():
    """Enable 2FA after verification"""
    data = request.get_json()
    
    if not data or not data.get('totp_token'):
        return jsonify({'error': 'TOTP token required'}), 400
    
    user = data_manager.get_user_by_id(request.user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    temp_secret = user.get('temp_totp_secret')
    if not temp_secret:
        return jsonify({'error': '2FA setup not initiated'}), 400
    
    if not security_manager.verify_totp(temp_secret, data['totp_token']):
        return jsonify({'error': 'Invalid TOTP token'}), 401
    
    # Enable 2FA
    user['totp_secret'] = temp_secret
    del user['temp_totp_secret']
    data_manager.save_data()
    
    # Send confirmation email
    email_service.send_2fa_setup_email(user['email'], user['name'], '')
    
    return jsonify({'message': '2FA enabled successfully'})

@api_bp.route('/auth/2fa/disable', methods=['POST'])
@require_api_auth
def api_disable_2fa():
    """Disable 2FA"""
    data = request.get_json()
    
    if not data or not data.get('totp_token'):
        return jsonify({'error': 'TOTP token required'}), 400
    
    user = data_manager.get_user_by_id(request.user_id)
    if not user or not user.get('totp_secret'):
        return jsonify({'error': '2FA not enabled'}), 400
    
    if not security_manager.verify_totp(user['totp_secret'], data['totp_token']):
        return jsonify({'error': 'Invalid TOTP token'}), 401
    
    # Disable 2FA
    del user['totp_secret']
    data_manager.save_data()
    
    return jsonify({'message': '2FA disabled successfully'})

@api_bp.route('/auth/password/reset', methods=['POST'])
def api_request_password_reset():
    """Request password reset"""
    data = request.get_json()
    
    if not data or not data.get('email'):
        return jsonify({'error': 'Email required'}), 400
    
    email = data['email']
    user = None
    
    # Find user by email
    for u in data_manager.get_all_users():
        if u['email'] == email:
            user = u
            break
    
    if not user:
        return jsonify({'message': 'If email exists, reset link will be sent'}), 200
    
    # Generate reset token
    reset_token = security_manager.generate_session_token()
    user['reset_token'] = reset_token
    user['reset_token_expires'] = (datetime.now() + timedelta(hours=24)).isoformat()
    data_manager.save_data()
    
    # Send reset email
    email_service.send_password_reset_email(email, reset_token, user['name'])
    
    return jsonify({'message': 'If email exists, reset link will be sent'})

@api_bp.route('/auth/password/reset/confirm', methods=['POST'])
def api_confirm_password_reset():
    """Confirm password reset"""
    data = request.get_json()
    
    if not data or not data.get('token') or not data.get('new_password'):
        return jsonify({'error': 'Token and new password required'}), 400
    
    token = data['token']
    new_password = data['new_password']
    
    # Find user with reset token
    user = None
    for u in data_manager.get_all_users():
        if u.get('reset_token') == token:
            user = u
            break
    
    if not user:
        return jsonify({'error': 'Invalid reset token'}), 400
    
    # Check if token expired
    if user.get('reset_token_expires'):
        expires = datetime.fromisoformat(user['reset_token_expires'])
        if datetime.now() > expires:
            return jsonify({'error': 'Reset token expired'}), 400
    
    # Validate password strength
    password_validation = security_manager.validate_password_strength(new_password)
    if not password_validation['valid']:
        return jsonify({
            'error': 'Password does not meet requirements',
            'details': password_validation['errors']
        }), 400
    
    # Update password
    user['password'] = security_manager.hash_password(new_password)
    del user['reset_token']
    del user['reset_token_expires']
    data_manager.save_data()
    
    return jsonify({'message': 'Password reset successfully'})

@api_bp.route('/auth/profile', methods=['GET'])
@require_api_auth
def api_get_profile():
    """Get user profile"""
    user = data_manager.get_user_by_id(request.user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user['id'],
        'name': user['name'],
        'email': user['email'],
        'role': user['role'],
        'department': user.get('department'),
        'created_at': user.get('created_at'),
        'has_2fa': bool(user.get('totp_secret'))
    })

@api_bp.route('/auth/profile', methods=['PUT'])
@require_api_auth
def api_update_profile():
    """Update user profile"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    user = data_manager.get_user_by_id(request.user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Update allowed fields
    updates = {}
    if 'name' in data:
        updates['name'] = data['name']
    if 'email' in data:
        updates['email'] = data['email']
    
    if updates:
        updated_user = data_manager.update_user(request.user_id, updates)
        if updated_user:
            return jsonify({
                'message': 'Profile updated successfully',
                'user': {
                    'id': updated_user['id'],
                    'name': updated_user['name'],
                    'email': updated_user['email'],
                    'role': updated_user['role'],
                    'department': updated_user.get('department')
                }
            })
    
    return jsonify({'error': 'No valid updates provided'}), 400

