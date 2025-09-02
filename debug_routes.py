#!/usr/bin/env python3
"""
Debug Routes for Trivanta ERP
=============================

This script adds debug routes to help identify issues.
"""

from flask import Blueprint, jsonify, current_app

debug_bp = Blueprint('debug', __name__)

@debug_bp.route('/debug/clients')
def debug_clients():
    """Debug route to test clients data"""
    try:
        clients = current_app.data_manager.get_all_clients()
        return jsonify({
            'success': True,
            'clients_count': len(clients),
            'clients': clients,
            'data_keys': list(current_app.data_manager.data.keys())
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__,
            'data_keys': list(current_app.data_manager.data.keys()) if hasattr(current_app, 'data_manager') else []
        })

@debug_bp.route('/debug/tasks')
def debug_tasks():
    """Debug route to test tasks data"""
    try:
        projects = current_app.data_manager.get_all_projects()
        return jsonify({
            'success': True,
            'projects_count': len(projects),
            'projects': projects,
            'data_keys': list(current_app.data_manager.data.keys())
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__,
            'data_keys': list(current_app.data_manager.data.keys()) if hasattr(current_app, 'data_manager') else []
        })

@debug_bp.route('/debug/data-structure')
def debug_data_structure():
    """Debug route to show data structure"""
    try:
        data = current_app.data_manager.data
        return jsonify({
            'success': True,
            'data_keys': list(data.keys()),
            'users_count': len(data.get('users', [])),
            'clients_count': len(data.get('clients', [])),
            'projects_count': len(data.get('projects', [])),
            'leads_count': len(data.get('leads', [])),
            'attendance_count': len(data.get('attendance', []))
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        })
