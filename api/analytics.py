from flask import request, jsonify
from utils.analytics_engine import AnalyticsEngine
from utils.data_manager import DataManager
from .auth import require_api_auth
from . import api_bp

data_manager = DataManager()
# Initialize analytics engine lazily to avoid app context issues
analytics_engine = None

def get_analytics_engine():
    global analytics_engine
    if analytics_engine is None:
        analytics_engine = AnalyticsEngine(data_manager)
    return analytics_engine

@api_bp.route('/analytics/comprehensive', methods=['GET'])
@require_api_auth
def api_get_comprehensive_analytics():
    """Get comprehensive analytics"""
    try:
        engine = get_analytics_engine()
        analytics = engine.get_comprehensive_analytics()
        return jsonify(analytics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/analytics/overview', methods=['GET'])
@require_api_auth
def api_get_overview_analytics():
    """Get overview analytics"""
    try:
        engine = get_analytics_engine()
        analytics = engine.get_comprehensive_analytics()
        return jsonify(analytics['overview'])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/analytics/financial', methods=['GET'])
@require_api_auth
def api_get_financial_analytics():
    """Get financial analytics"""
    try:
        engine = get_analytics_engine()
        analytics = engine.get_comprehensive_analytics()
        return jsonify(analytics['financial'])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/analytics/operational', methods=['GET'])
@require_api_auth
def api_get_operational_analytics():
    """Get operational analytics"""
    try:
        engine = get_analytics_engine()
        analytics = engine.get_comprehensive_analytics()
        return jsonify(analytics['operational'])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/analytics/performance', methods=['GET'])
@require_api_auth
def api_get_performance_analytics():
    """Get performance analytics"""
    try:
        engine = get_analytics_engine()
        analytics = engine.get_comprehensive_analytics()
        return jsonify(analytics['performance'])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/analytics/trends', methods=['GET'])
@require_api_auth
def api_get_trend_analytics():
    """Get trend analytics"""
    try:
        engine = get_analytics_engine()
        analytics = engine.get_comprehensive_analytics()
        return jsonify(analytics['trends'])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/analytics/predictions', methods=['GET'])
@require_api_auth
def api_get_predictive_analytics():
    """Get predictive analytics"""
    try:
        engine = get_analytics_engine()
        analytics = engine.get_comprehensive_analytics()
        return jsonify(analytics['predictions'])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/analytics/charts', methods=['GET'])
@require_api_auth
def api_get_charts():
    """Get analytics charts"""
    try:
        engine = get_analytics_engine()
        analytics = engine.get_comprehensive_analytics()
        return jsonify(analytics['charts'])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/analytics/reports/<report_type>', methods=['GET'])
@require_api_auth
def api_generate_report(report_type):
    """Generate custom reports"""
    try:
        filters = request.args.to_dict()
        engine = get_analytics_engine()
        report = engine.generate_custom_report(report_type, filters)
        return jsonify(report)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/analytics/cache/clear', methods=['POST'])
@require_api_auth
def api_clear_analytics_cache():
    """Clear analytics cache"""
    try:
        if request.user_role not in ['admin']:
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        engine = get_analytics_engine()
        engine.clear_cache()
        return jsonify({'message': 'Analytics cache cleared successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
