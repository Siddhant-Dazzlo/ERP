from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, current_app
from utils.auth import employee_required
from utils.security import SecurityManager
from datetime import datetime, timedelta

employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/dashboard')
@employee_required
def dashboard():
    """Employee dashboard with personal overview"""
    user_id = session.get('user_id')
    user = current_app.data_manager.get_user_by_id(user_id)
    
    # Get employee's assigned projects
    projects = current_app.data_manager.get_all_projects()
    assigned_projects = [p for p in projects if user_id in p.get('assigned_employees', [])]
    
    # Get employee's attendance for today
    today = datetime.now().strftime('%Y-%m-%d')
    today_attendance = None
    for record in current_app.data_manager.data['attendance']:
        if record['employee_id'] == user_id and record['date'] == today:
            today_attendance = record
            break
    
    context = {
        'user': user,
        'assigned_projects': assigned_projects,
        'today_attendance': today_attendance,
        'today': today
    }
    
    return render_template('employee/dashboard.html', **context)

@employee_bp.route('/attendance')
@employee_required
def attendance():
    """Employee attendance page"""
    user_id = session.get('user_id')
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Get today's attendance record
    today_attendance = None
    for record in current_app.data_manager.data['attendance']:
        if record['employee_id'] == user_id and record['date'] == today:
            today_attendance = record
            break
    
    # Get attendance history
    attendance_history = [r for r in current_app.data_manager.data['attendance'] if r['employee_id'] == user_id]
    attendance_history.sort(key=lambda x: x['date'], reverse=True)
    
    context = {
        'today_attendance': today_attendance,
        'attendance_history': attendance_history[:10],  # Last 10 records
        'today': today
    }
    
    return render_template('employee/attendance.html', **context)

@employee_bp.route('/attendance/check-in', methods=['POST'])
@employee_required
def check_in():
    """Employee check-in with OTP"""
    user_id = session.get('user_id')
    otp = request.form.get('otp')
    
    # Verify OTP against daily OTP
    if current_app.data_manager.verify_otp(otp):
        attendance_data = {
            'employee_id': user_id,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'check_in': datetime.now().strftime('%H:%M:%S'),
            'otp_used': otp,
            'location': 'Office'  # In real system, get from GPS
        }
        
        current_app.data_manager.create_attendance_record(attendance_data)
        flash('Check-in successful!', 'success')
    else:
        flash('Invalid OTP. Please try again.', 'error')
    
    return redirect(url_for('employee.attendance'))

@employee_bp.route('/attendance/check-out', methods=['POST'])
@employee_required
def check_out():
    """Employee check-out with OTP"""
    user_id = session.get('user_id')
    otp = request.form.get('otp')
    
    # Verify OTP against daily OTP
    if current_app.data_manager.verify_otp(otp):
        # Find today's attendance record and update check-out time
        today = datetime.now().strftime('%Y-%m-%d')
        for record in current_app.data_manager.data['attendance']:
            if record['employee_id'] == user_id and record['date'] == today:
                record['check_out'] = datetime.now().strftime('%H:%M:%S')
                current_app.data_manager.save_data()
                flash('Check-out successful!', 'success')
                break
        else:
            flash('No check-in record found for today.', 'error')
    else:
        flash('Invalid OTP. Please try again.', 'error')
    
    return redirect(url_for('employee.attendance'))

@employee_bp.route('/leads')
@employee_required
def leads():
    """Employee lead management page"""
    user_id = session.get('user_id')
    leads = current_app.data_manager.get_all_leads()
    
    # Filter leads assigned to this employee
    assigned_leads = [lead for lead in leads if lead.get('assigned_to') == user_id]
    
    return render_template('employee/leads.html', leads=assigned_leads)

@employee_bp.route('/leads/create', methods=['GET', 'POST'])
@employee_required
def create_lead():
    """Create new lead"""
    if request.method == 'POST':
        lead_data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'company': request.form.get('company'),
            'business_type': request.form.get('business_type'),
            'source': request.form.get('source'),
            'assigned_to': session.get('user_id'),
            'notes': request.form.get('notes'),
            'created_by': session.get('user_id')
        }
        
        new_lead = current_app.data_manager.create_lead(lead_data)
        flash(f'Lead {new_lead["name"]} created successfully.', 'success')
        return redirect(url_for('employee.leads'))
    
    return render_template('employee/create_lead.html')

@employee_bp.route('/clients')
@employee_required
def clients():
    """Employee client management page"""
    user_id = session.get('user_id')
    clients = current_app.data_manager.get_all_clients()
    
    # Filter clients created by this employee (if tracking is needed)
    # For now, show all clients
    return render_template('employee/clients.html', clients=clients)

@employee_bp.route('/clients/create', methods=['GET', 'POST'])
@employee_required
def create_client():
    """Create new client"""
    if request.method == 'POST':
        client_data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'company': request.form.get('company'),
            'business_type': request.form.get('business_type'),
            'address': request.form.get('address')
        }
        
        new_client = current_app.data_manager.create_client(client_data)
        flash(f'Client {new_client["name"]} created successfully.', 'success')
        return redirect(url_for('employee.clients'))
    
    return render_template('employee/create_client.html')

@employee_bp.route('/projects')
@employee_required
def projects():
    """Employee project overview page"""
    user_id = session.get('user_id')
    projects = current_app.data_manager.get_all_projects()
    
    # Filter projects assigned to this employee
    assigned_projects = [p for p in projects if user_id in p.get('assigned_employees', [])]
    
    return render_template('employee/projects.html', projects=assigned_projects)

@employee_bp.route('/projects/<project_id>')
@employee_required
def project_detail(project_id):
    """View project details"""
    user_id = session.get('user_id')
    project = None
    
    for p in current_app.data_manager.get_all_projects():
        if p['id'] == project_id and user_id in p.get('assigned_employees', []):
            project = p
            break
    
    if not project:
        flash('Project not found or access denied.', 'error')
        return redirect(url_for('employee.projects'))
    
    # Get client information
    client = None
    for c in current_app.data_manager.get_all_clients():
        if c['id'] == project['client_id']:
            client = c
            break
    
    context = {
        'project': project,
        'client': client
    }
    
    return render_template('employee/project_detail.html', **context)

@employee_bp.route('/tasks')
@employee_required
def tasks():
    """Employee task management page"""
    user_id = session.get('user_id')
    projects = current_app.data_manager.get_all_projects()
    
    # Get tasks from assigned projects
    tasks = []
    for project in projects:
        if user_id in project.get('assigned_employees', []):
            tasks.append({
                'id': project['id'],
                'name': project['name'],
                'type': project['type'],
                'status': project['status'],
                'description': project.get('description', ''),
                'start_date': project.get('start_date', ''),
                'end_date': project.get('end_date', '')
            })
    
    return render_template('employee/tasks.html', tasks=tasks)

@employee_bp.route('/reports')
@employee_required
def reports():
    """Employee reports page"""
    user_id = session.get('user_id')
    user = current_app.data_manager.get_user_by_id(user_id)
    
    # Get employee's performance data
    projects = current_app.data_manager.get_all_projects()
    assigned_projects = [p for p in projects if user_id in p.get('assigned_employees', [])]
    
    # Calculate basic metrics
    total_projects = len(assigned_projects)
    completed_projects = len([p for p in assigned_projects if p['status'] == 'completed'])
    pending_projects = len([p for p in assigned_projects if p['status'] == 'pending'])
    
    context = {
        'user': user,
        'total_projects': total_projects,
        'completed_projects': completed_projects,
        'pending_projects': pending_projects,
        'recent_projects': assigned_projects[-5:] if assigned_projects else []
    }
    
    return render_template('employee/reports.html', **context)

@employee_bp.route('/profile')
@employee_required
def profile():
    """Employee profile page"""
    user_id = session.get('user_id')
    user = current_app.data_manager.get_user_by_id(user_id)
    
    return render_template('employee/profile.html', user=user)

@employee_bp.route('/profile/edit', methods=['GET', 'POST'])
@employee_required
def edit_profile():
    """Edit employee profile"""
    user_id = session.get('user_id')
    user = current_app.data_manager.get_user_by_id(user_id)
    
    if request.method == 'POST':
        # Initialize security manager
        security_manager = SecurityManager()
        
        updates = {
            'name': request.form.get('name'),
            'email': request.form.get('email')
        }
        
        if request.form.get('password'):
            updates['password'] = security_manager.hash_password(request.form.get('password'))  # Hash the password
        
        updated_user = current_app.data_manager.update_user(user_id, updates)
        if updated_user:
            session['name'] = updated_user['name']
            flash('Profile updated successfully.', 'success')
            return redirect(url_for('employee.profile'))
    
    return render_template('employee/edit_profile.html', user=user)

@employee_bp.route('/api/my-projects')
@employee_required
def api_my_projects():
    """API endpoint for employee's assigned projects"""
    user_id = session.get('user_id')
    projects = current_app.data_manager.get_all_projects()
    assigned_projects = [p for p in projects if user_id in p.get('assigned_employees', [])]
    return jsonify(assigned_projects)
