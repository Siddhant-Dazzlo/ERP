from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_session import Session
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta
import secrets
from functools import wraps

# Import configuration
from config import config

# Import route modules
from routes.admin import admin_bp
from routes.manager import manager_bp
from routes.employee import employee_bp
from debug_routes import debug_bp

# Import API modules
from api import api_bp

# Import utility modules
from utils.auth import login_required, role_required
from utils.firebase_data_manager import FirebaseDataManager
from utils.security import security_manager
from utils.email_service import email_service
from utils.file_manager import file_manager
from utils.analytics_engine import AnalyticsEngine
from utils.websocket_manager import websocket_manager

def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    Session(app)
    CORS(app)
    
    # Initialize Firebase data manager
    data_manager = FirebaseDataManager()
    app.data_manager = data_manager
    
    # Initialize analytics engine
    analytics_engine = AnalyticsEngine(data_manager)
    app.analytics_engine = analytics_engine
    
    # Initialize WebSocket manager
    websocket_manager.init_app(app)
    app.websocket_manager = websocket_manager
    
    # Initialize email service
    email_service.init_app(app)
    app.email_service = email_service
    
    # Initialize file manager
    app.file_manager = file_manager
    
    # Register blueprints
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(manager_bp, url_prefix='/manager')
    app.register_blueprint(employee_bp, url_prefix='/employee')
    app.register_blueprint(api_bp)
    app.register_blueprint(debug_bp, url_prefix='/debug')
    
    # Initialize default data
    data_manager.initialize_default_data()
    
    # Start background tasks
    websocket_manager.run_background_tasks()
    
    return app

# Create application instance
app = create_app()

# Initialize Railway data if needed
if os.environ.get('RAILWAY_ENVIRONMENT'):
    try:
        print("🚀 Running on Railway - initializing data...")
        from initialize_railway_data import create_railway_data
        create_railway_data()
        print("✅ Railway data initialization completed")
    except Exception as e:
        print(f"⚠️ Railway data initialization failed: {e}")

# Add startup delay for Railway
@app.before_request
def startup_delay():
    """Add a small delay for Railway to properly initialize"""
    if not hasattr(app, '_startup_completed'):
        import time
        time.sleep(2)
        app._startup_completed = True
        print("✅ App startup delay completed")

@app.route('/')
def index():
    if 'user_id' in session:
        role = session.get('role')
        if role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif role == 'manager':
            return redirect(url_for('manager.dashboard'))
        elif role == 'employee':
            return redirect(url_for('employee.dashboard'))
    return redirect(url_for('login'))

@app.route('/health')
def health_check():
    """Simple health check for Railway"""
    try:
        # Basic system check
        status = "healthy"
        message = "Trivanta Edge ERP is running"
        
        # Check if data manager is working
        if hasattr(app, 'data_manager') and app.data_manager:
            data_status = "Data manager: OK"
        else:
            data_status = "Data manager: Not available"
            status = "degraded"
        
        return jsonify({
            'status': status,
            'message': message,
            'data_status': data_status,
            'timestamp': datetime.now().isoformat(),
            'railway_ready': True
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Health check failed: {str(e)}',
            'timestamp': datetime.now().isoformat(),
            'railway_ready': False
        }), 500

@app.route('/test')
def test_template():
    """Test route to verify template rendering"""
    return render_template('test.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check for admin login
        if email == 'admin@trivantaedge.com' and password == 'As@102005':
            session['user_id'] = 'admin_001'
            session['role'] = 'admin'
            session['name'] = 'Siddhant_MD'
            session.permanent = True
            return redirect(url_for('admin.dashboard'))
        
        # Check manager/employee credentials with enhanced security
        user = app.data_manager.authenticate_user(email, password)
        if user:
            # Check if 2FA is required
            if user.get('totp_secret'):
                session['temp_user_id'] = user['id']
                session['temp_user_role'] = user['role']
                session['temp_user_name'] = user['name']
                session['requires_2fa'] = True
                return redirect(url_for('verify_2fa'))
            
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['name'] = user['name']
            session.permanent = True
            
            # Send welcome notification via WebSocket
            app.websocket_manager.send_notification(user['id'], {
                'type': 'login_success',
                'message': f'Welcome back, {user["name"]}!',
                'timestamp': datetime.now().isoformat()
            })
            
            return redirect(url_for(f'{user["role"]}.dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/verify-2fa', methods=['GET', 'POST'])
def verify_2fa():
    if not session.get('requires_2fa'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        totp_token = request.form.get('totp_token')
        user_id = session.get('temp_user_id')
        
        if user_id and totp_token:
            user = app.data_manager.get_user_by_id(user_id)
            if user and user.get('totp_secret'):
                if security_manager.verify_totp(user['totp_secret'], totp_token):
                    # 2FA successful, complete login
                    session['user_id'] = user['id']
                    session['role'] = user['role']
                    session['name'] = user['name']
                    session.permanent = True
                    
                    # Clear temporary session data
                    session.pop('temp_user_id', None)
                    session.pop('temp_user_role', None)
                    session.pop('temp_user_name', None)
                    session.pop('requires_2fa', None)
                    
                    # Send welcome notification
                    app.websocket_manager.send_notification(user['id'], {
                        'type': 'login_success',
                        'message': f'Welcome back, {user["name"]}!',
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    return redirect(url_for(f'{user["role"]}.dashboard'))
                else:
                    flash('Invalid 2FA token. Please try again.', 'error')
            else:
                flash('2FA verification failed. Please try again.', 'error')
        else:
            flash('Please enter your 2FA token.', 'error')
    
    return render_template('verify_2fa.html')

@app.route('/logout')
def logout():
    user_id = session.get('user_id')
    if user_id:
        # Send logout notification
        app.websocket_manager.send_notification(user_id, {
            'type': 'logout',
            'message': 'You have been logged out successfully.',
            'timestamp': datetime.now().isoformat()
        })
    
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/setup-2fa', methods=['GET', 'POST'])
@login_required
def setup_2fa():
    user_id = session.get('user_id')
    user = app.data_manager.get_user_by_id(user_id)
    
    if user.get('totp_secret'):
        flash('2FA is already enabled for your account.', 'info')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'setup':
            # Generate new TOTP secret
            totp_secret = security_manager.generate_totp_secret()
            qr_code = security_manager.generate_totp_qr_code(totp_secret, user['email'])
            
            # Store temporarily
            user['temp_totp_secret'] = totp_secret
            app.data_manager.save_data()
            
            return render_template('setup_2fa.html', qr_code=qr_code, totp_secret=totp_secret)
        
        elif action == 'verify':
            totp_token = request.form.get('totp_token')
            temp_secret = user.get('temp_totp_secret')
            
            if temp_secret and security_manager.verify_totp(temp_secret, totp_token):
                # Enable 2FA
                user['totp_secret'] = temp_secret
                del user['temp_totp_secret']
                app.data_manager.save_data()
                
                # Send confirmation email
                app.email_service.send_2fa_setup_email(user['email'], user['name'], '')
                
                flash('2FA has been enabled successfully!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid 2FA token. Please try again.', 'error')
    
    return render_template('setup_2fa.html')

@app.route('/file-upload', methods=['POST'])
@login_required
def file_upload():
    """Handle file uploads"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get metadata
        metadata = {
            'uploaded_by': session.get('user_id'),
            'category': request.form.get('category', 'documents'),
            'description': request.form.get('description', '')
        }
        
        # Upload file
        file_record = app.file_manager.upload_file(file, metadata=metadata)
        
        # Send notification
        app.websocket_manager.send_notification(session.get('user_id'), {
            'type': 'file_uploaded',
            'message': f'File {file_record["original_filename"]} uploaded successfully',
            'file_data': file_record
        })
        
        return jsonify({
            'message': 'File uploaded successfully',
            'file': file_record
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/health')
def api_health_check():
    return jsonify({
        'status': 'healthy', 
        'system': 'Trivanta Edge ERP',
        'version': '2.0.0',
        'features': {
            'websocket': True,
            'api': True,
            '2fa': True,
            'email': True,
            'file_upload': True,
            'analytics': True
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/analytics/comprehensive')
@login_required
def api_comprehensive_analytics():
    """Get comprehensive analytics via API"""
    try:
        analytics = app.analytics_engine.get_comprehensive_analytics()
        return jsonify(analytics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/report/<report_type>')
@login_required
def api_generate_report(report_type):
    """Generate custom reports via API"""
    try:
        filters = request.args.to_dict()
        report = app.analytics_engine.generate_custom_report(report_type, filters)
        return jsonify(report)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

@app.errorhandler(413)
def file_too_large(error):
    return jsonify({'error': 'File too large'}), 413

# WebSocket events
@websocket_manager.socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    user_id = request.args.get('user_id')
    role = request.args.get('role')
    
    if user_id and role:
        app.websocket_manager.handle_connect()

@websocket_manager.socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    app.websocket_manager.handle_disconnect()

if __name__ == '__main__':
    try:
        # Get port from environment variable (for Railway) or use default
        port = int(os.environ.get('PORT', 8080))
        print(f"🚀 Starting Trivanta Edge ERP on port {port}")
        
        # Initialize components with error handling
        print("📋 Initializing WebSocket manager...")
        socketio = websocket_manager.socketio
        
        print("📋 Starting Flask app...")
        socketio.run(app, debug=False, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
        
    except Exception as e:
        print(f"❌ Failed to start app: {e}")
        import traceback
        traceback.print_exc()
        # Fallback: start without WebSocket
        try:
            print("🔄 Attempting fallback startup...")
            app.run(debug=False, host='0.0.0.0', port=port)
        except Exception as fallback_error:
            print(f"❌ Fallback also failed: {fallback_error}")
            traceback.print_exc()
