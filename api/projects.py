from flask import request, jsonify
from datetime import datetime
from utils.data_manager import DataManager
from utils.websocket_manager import websocket_manager
from .auth import require_api_auth
from . import api_bp

data_manager = DataManager()

@api_bp.route('/projects', methods=['GET'])
@require_api_auth
def api_get_projects():
    """Get all projects"""
    try:
        projects = data_manager.get_all_projects()
        
        # Filter by user role
        if request.user_role == 'employee':
            # Employees only see assigned projects
            projects = [p for p in projects if request.user_id in p.get('assigned_employees', [])]
        
        return jsonify({
            'projects': projects,
            'total': len(projects)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/projects/<project_id>', methods=['GET'])
@require_api_auth
def api_get_project(project_id):
    """Get specific project"""
    try:
        project = data_manager.get_project_by_id(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Check access permissions
        if request.user_role == 'employee' and request.user_id not in project.get('assigned_employees', []):
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({'project': project})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/projects', methods=['POST'])
@require_api_auth
def api_create_project():
    """Create new project"""
    try:
        if request.user_role not in ['admin', 'manager']:
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['name', 'type', 'client_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create project
        project_data = {
            'name': data['name'],
            'type': data['type'],
            'client_id': data['client_id'],
            'description': data.get('description', ''),
            'start_date': data.get('start_date', ''),
            'end_date': data.get('end_date', ''),
            'budget': float(data.get('budget', 0)),
            'assigned_employees': data.get('assigned_employees', []),
            'created_by': request.user_id
        }
        
        new_project = data_manager.create_project(project_data)
        
        # Send real-time notification
        websocket_manager.send_project_update(new_project['id'], 'created', new_project)
        
        return jsonify({
            'message': 'Project created successfully',
            'project': new_project
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/projects/<project_id>', methods=['PUT'])
@require_api_auth
def api_update_project(project_id):
    """Update project"""
    try:
        project = data_manager.get_project_by_id(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Check permissions
        if request.user_role == 'employee':
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update project
        updated_project = data_manager.update_project(project_id, data)
        if not updated_project:
            return jsonify({'error': 'Failed to update project'}), 500
        
        # Send real-time notification
        websocket_manager.send_project_update(project_id, 'updated', updated_project)
        
        return jsonify({
            'message': 'Project updated successfully',
            'project': updated_project
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/projects/<project_id>', methods=['DELETE'])
@require_api_auth
def api_delete_project(project_id):
    """Delete project"""
    try:
        if request.user_role not in ['admin', 'manager']:
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        project = data_manager.get_project_by_id(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Soft delete
        success = data_manager.delete_project(project_id)
        if not success:
            return jsonify({'error': 'Failed to delete project'}), 500
        
        # Send real-time notification
        websocket_manager.send_project_update(project_id, 'deleted', project)
        
        return jsonify({'message': 'Project deleted successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/projects/<project_id>/assign', methods=['POST'])
@require_api_auth
def api_assign_project(project_id):
    """Assign employees to project"""
    try:
        if request.user_role not in ['admin', 'manager']:
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        project = data_manager.get_project_by_id(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        data = request.get_json()
        if not data or 'employee_ids' not in data:
            return jsonify({'error': 'Employee IDs required'}), 400
        
        # Update assigned employees
        updates = {'assigned_employees': data['employee_ids']}
        updated_project = data_manager.update_project(project_id, updates)
        
        if not updated_project:
            return jsonify({'error': 'Failed to assign employees'}), 500
        
        # Send real-time notification
        websocket_manager.send_project_update(project_id, 'assigned', updated_project)
        
        return jsonify({
            'message': 'Employees assigned successfully',
            'project': updated_project
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/projects/<project_id>/status', methods=['PUT'])
@require_api_auth
def api_update_project_status(project_id):
    """Update project status"""
    try:
        project = data_manager.get_project_by_id(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Check permissions
        if request.user_role == 'employee' and request.user_id not in project.get('assigned_employees', []):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({'error': 'Status required'}), 400
        
        # Validate status
        valid_statuses = ['pending', 'in_progress', 'completed', 'on_hold', 'cancelled']
        if data['status'] not in valid_statuses:
            return jsonify({'error': 'Invalid status'}), 400
        
        # Update status
        updates = {'status': data['status']}
        updated_project = data_manager.update_project(project_id, updates)
        
        if not updated_project:
            return jsonify({'error': 'Failed to update status'}), 500
        
        # Send real-time notification
        websocket_manager.send_project_update(project_id, 'status_changed', updated_project)
        
        return jsonify({
            'message': 'Project status updated successfully',
            'project': updated_project
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/projects/my-projects', methods=['GET'])
@require_api_auth
def api_get_my_projects():
    """Get projects assigned to current user"""
    try:
        if request.user_role == 'employee':
            projects = data_manager.get_all_projects()
            my_projects = [p for p in projects if request.user_id in p.get('assigned_employees', [])]
            
            return jsonify({
                'projects': my_projects,
                'total': len(my_projects)
            })
        else:
            return jsonify({'error': 'This endpoint is for employees only'}), 403
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/projects/statistics', methods=['GET'])
@require_api_auth
def api_get_project_statistics():
    """Get project statistics"""
    try:
        projects = data_manager.get_all_projects()
        
        # Filter by user role
        if request.user_role == 'employee':
            projects = [p for p in projects if request.user_id in p.get('assigned_employees', [])]
        
        # Calculate statistics
        total_projects = len(projects)
        active_projects = len([p for p in projects if p.get('status') == 'in_progress'])
        completed_projects = len([p for p in projects if p.get('status') == 'completed'])
        pending_projects = len([p for p in projects if p.get('status') == 'pending'])
        
        total_revenue = sum(p.get('budget', 0) for p in projects)
        avg_project_value = total_revenue / total_projects if total_projects > 0 else 0
        
        return jsonify({
            'total_projects': total_projects,
            'active_projects': active_projects,
            'completed_projects': completed_projects,
            'pending_projects': pending_projects,
            'total_revenue': total_revenue,
            'average_project_value': avg_project_value,
            'completion_rate': (completed_projects / total_projects * 100) if total_projects > 0 else 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

