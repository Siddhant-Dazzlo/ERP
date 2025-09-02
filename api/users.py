from flask import request, jsonify
from utils.data_manager import DataManager
from utils.security import security_manager
from .auth import require_api_auth
from . import api_bp

data_manager = DataManager()

@api_bp.route('/users', methods=['GET'])
@require_api_auth
def api_get_users():
    """Get all users"""
    try:
        if request.user_role not in ['admin', 'manager']:
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        role_filter = request.args.get('role')
        users = data_manager.get_all_users(role=role_filter)
        
        return jsonify({
            'users': users,
            'total': len(users)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/users/<user_id>', methods=['GET'])
@require_api_auth
def api_get_user(user_id):
    """Get specific user"""
    try:
        # Users can only view their own profile unless admin/manager
        if request.user_role not in ['admin', 'manager'] and request.user_id != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        user = data_manager.get_user_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/users', methods=['POST'])
@require_api_auth
def api_create_user():
    """Create new user"""
    try:
        if request.user_role not in ['admin', 'manager']:
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['name', 'email', 'password', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate password strength
        password_validation = security_manager.validate_password_strength(data['password'])
        if not password_validation['valid']:
            return jsonify({
                'error': 'Password does not meet requirements',
                'details': password_validation['errors']
            }), 400
        
        # Hash password
        data['password'] = security_manager.hash_password(data['password'])
        
        # Create user
        new_user = data_manager.create_user(data)
        
        return jsonify({
            'message': 'User created successfully',
            'user': new_user
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/users/<user_id>', methods=['PUT'])
@require_api_auth
def api_update_user(user_id):
    """Update user"""
    try:
        # Users can only update their own profile unless admin/manager
        if request.user_role not in ['admin', 'manager'] and request.user_id != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        user = data_manager.get_user_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Hash password if provided
        if 'password' in data and data['password']:
            password_validation = security_manager.validate_password_strength(data['password'])
            if not password_validation['valid']:
                return jsonify({
                    'error': 'Password does not meet requirements',
                    'details': password_validation['errors']
                }), 400
            data['password'] = security_manager.hash_password(data['password'])
        
        # Update user
        updated_user = data_manager.update_user(user_id, data)
        if not updated_user:
            return jsonify({'error': 'Failed to update user'}), 500
        
        return jsonify({
            'message': 'User updated successfully',
            'user': updated_user
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/users/<user_id>', methods=['DELETE'])
@require_api_auth
def api_delete_user(user_id):
    """Delete user"""
    try:
        if request.user_role not in ['admin', 'manager']:
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        user = data_manager.get_user_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Soft delete
        success = data_manager.delete_user(user_id)
        if not success:
            return jsonify({'error': 'Failed to delete user'}), 500
        
        return jsonify({'message': 'User deleted successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/users/employees', methods=['GET'])
@require_api_auth
def api_get_employees():
    """Get all employees"""
    try:
        if request.user_role not in ['admin', 'manager']:
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        employees = data_manager.get_all_users(role='employee')
        
        return jsonify({
            'employees': employees,
            'total': len(employees)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/users/managers', methods=['GET'])
@require_api_auth
def api_get_managers():
    """Get all managers"""
    try:
        if request.user_role not in ['admin']:
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        managers = data_manager.get_all_users(role='manager')
        
        return jsonify({
            'managers': managers,
            'total': len(managers)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/users/statistics', methods=['GET'])
@require_api_auth
def api_get_user_statistics():
    """Get user statistics"""
    try:
        if request.user_role not in ['admin', 'manager']:
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        all_users = data_manager.get_all_users()
        employees = data_manager.get_all_users(role='employee')
        managers = data_manager.get_all_users(role='manager')
        
        active_users = len([u for u in all_users if u.get('status') == 'active'])
        inactive_users = len([u for u in all_users if u.get('status') == 'inactive'])
        
        # Department statistics
        departments = {}
        for user in all_users:
            dept = user.get('department', 'General')
            if dept not in departments:
                departments[dept] = 0
            departments[dept] += 1
        
        return jsonify({
            'total_users': len(all_users),
            'active_users': active_users,
            'inactive_users': inactive_users,
            'employees': len(employees),
            'managers': len(managers),
            'departments': departments
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

