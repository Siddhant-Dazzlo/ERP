from flask import request, jsonify, send_file
from utils.file_manager import get_file_manager
from .auth import require_api_auth
from . import api_bp
import os

@api_bp.route('/files', methods=['GET'])
@require_api_auth
def api_get_files():
    """Get all files"""
    try:
        category = request.args.get('category')
        uploaded_by = request.args.get('uploaded_by')
        
        # Get storage stats
        fm = get_file_manager()
        stats = fm.get_storage_stats()
        
        # In a real implementation, you would query a database for file records
        # For now, we'll return the storage stats
        return jsonify({
            'files': [],  # Placeholder for file records
            'statistics': stats,
            'total': stats['file_count']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/files/upload', methods=['POST'])
@require_api_auth
def api_upload_file():
    """Upload file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get metadata
        metadata = {
            'uploaded_by': request.user_id,
            'category': request.form.get('category', 'documents'),
            'description': request.form.get('description', '')
        }
        
        # Upload file
        fm = get_file_manager()
        file_record = fm.upload_file(file, metadata=metadata)
        
        return jsonify({
            'message': 'File uploaded successfully',
            'file': file_record
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api_bp.route('/files/<file_id>', methods=['GET'])
@require_api_auth
def api_get_file(file_id):
    """Get file information"""
    try:
        # In a real implementation, you would query a database for file records
        # For now, we'll return a placeholder
        return jsonify({
            'error': 'File not found'
        }), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/files/<file_id>/download', methods=['GET'])
@require_api_auth
def api_download_file(file_id):
    """Download file"""
    try:
        # In a real implementation, you would query a database for file records
        # and return the actual file
        return jsonify({
            'error': 'File not found'
        }), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/files/<file_id>', methods=['DELETE'])
@require_api_auth
def api_delete_file(file_id):
    """Delete file"""
    try:
        # In a real implementation, you would query a database for file records
        # and delete the actual file
        return jsonify({
            'error': 'File not found'
        }), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/files/statistics', methods=['GET'])
@require_api_auth
def api_get_file_statistics():
    """Get file storage statistics"""
    try:
        fm = get_file_manager()
        stats = fm.get_storage_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/files/cleanup', methods=['POST'])
@require_api_auth
def api_cleanup_files():
    """Clean up temporary files"""
    try:
        if request.user_role not in ['admin']:
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        max_age_hours = request.json.get('max_age_hours', 24)
        fm = get_file_manager()
        deleted_count = fm.cleanup_temp_files(max_age_hours)
        
        return jsonify({
            'message': f'Cleaned up {deleted_count} temporary files',
            'deleted_count': deleted_count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
