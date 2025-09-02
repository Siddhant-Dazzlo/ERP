from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, current_app
from utils.auth import manager_required
from utils.security import SecurityManager
from datetime import datetime, timedelta

manager_bp = Blueprint('manager', __name__)

@manager_bp.route('/dashboard')
@manager_required
def dashboard():
    """Manager dashboard with team overview"""
    user_id = session.get('user_id')
    analytics = current_app.data_manager.get_analytics()
    
    # Get projects assigned to manager's team
    projects = current_app.data_manager.get_all_projects()
    clients = current_app.data_manager.get_all_clients()
    employees = current_app.data_manager.get_all_users(role='employee')
    
    context = {
        'analytics': analytics,
        'total_projects': len(projects),
        'total_clients': len(clients),
        'total_employees': len(employees),
        'recent_projects': projects[-5:] if projects else [],
        'recent_clients': clients[-5:] if clients else []
    }
    
    return render_template('manager/dashboard.html', **context)

@manager_bp.route('/employees')
@manager_required
def employees():
    """Employee management page"""
    employees = current_app.data_manager.get_all_users(role='employee')
    return render_template('manager/employees.html', employees=employees)

@manager_bp.route('/employees/create', methods=['GET', 'POST'])
@manager_required
def create_employee():
    """Create new employee"""
    if request.method == 'POST':
        # Initialize security manager
        security_manager = SecurityManager()
        
        user_data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'password': security_manager.hash_password(request.form.get('password')),  # Hash the password
            'role': 'employee',
            'department': request.form.get('department')
        }
        
        new_user = current_app.data_manager.create_user(user_data)
        flash(f'Employee {new_user["name"]} created successfully.', 'success')
        return redirect(url_for('manager.employees'))
    
    return render_template('manager/create_employee.html')

@manager_bp.route('/employees/<user_id>/edit', methods=['GET', 'POST'])
@manager_required
def edit_employee(user_id):
    """Edit existing employee"""
    user = current_app.data_manager.get_user_by_id(user_id)
    if not user or user['role'] != 'employee':
        flash('Employee not found.', 'error')
        return redirect(url_for('manager.employees'))
    
    if request.method == 'POST':
        # Initialize security manager
        security_manager = SecurityManager()
        
        updates = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'department': request.form.get('department')
        }
        
        if request.form.get('password'):
            updates['password'] = security_manager.hash_password(request.form.get('password'))  # Hash the password
        
        updated_user = current_app.data_manager.update_user(user_id, updates)
        if updated_user:
            flash('Employee updated successfully.', 'success')
            return redirect(url_for('manager.employees'))
    
    return render_template('manager/edit_employee.html', user=user)

@manager_bp.route('/projects')
@manager_required
def projects():
    """Project management page"""
    projects = current_app.data_manager.get_all_projects()
    return render_template('manager/projects.html', projects=projects)

@manager_bp.route('/projects/create', methods=['GET', 'POST'])
@manager_required
def create_project():
    """Create new project"""
    if request.method == 'POST':
        project_data = {
            'name': request.form.get('name'),
            'type': request.form.get('type'),
            'client_id': request.form.get('client_id'),
            'description': request.form.get('description'),
            'start_date': request.form.get('start_date'),
            'end_date': request.form.get('end_date'),
            'budget': float(request.form.get('budget', 0)),
            'assigned_employees': request.form.getlist('assigned_employees'),
            'created_by': session.get('user_id')
        }
        
        new_project = current_app.data_manager.create_project(project_data)
        flash(f'Project {new_project["name"]} created successfully.', 'success')
        return redirect(url_for('manager.projects'))
    
    clients = current_app.data_manager.get_all_clients()
    employees = current_app.data_manager.get_all_users(role='employee')
    return render_template('manager/create_project.html', clients=clients, employees=employees)

@manager_bp.route('/clients')
@manager_required
def clients():
    """Client management page"""
    clients = current_app.data_manager.get_all_clients()
    return render_template('manager/clients.html', clients=clients)

@manager_bp.route('/clients/create', methods=['GET', 'POST'])
@manager_required
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
        return redirect(url_for('manager.clients'))
    
    return render_template('manager/create_client.html')

@manager_bp.route('/leads')
@manager_required
def leads():
    """Lead management page"""
    leads = current_app.data_manager.get_all_leads()
    return render_template('manager/leads.html', leads=leads)

@manager_bp.route('/leads/create', methods=['GET', 'POST'])
@manager_required
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
            'assigned_to': request.form.get('assigned_to'),
            'notes': request.form.get('notes'),
            'created_by': session.get('user_id')
        }
        
        new_lead = current_app.data_manager.create_lead(lead_data)
        flash(f'Lead {new_lead["name"]} created successfully.', 'success')
        return redirect(url_for('manager.leads'))
    
    employees = current_app.data_manager.get_all_users(role='employee')
    return render_template('manager/create_lead.html', employees=employees)

@manager_bp.route('/attendance')
@manager_required
def attendance():
    """Attendance management page"""
    today = datetime.now().strftime('%Y-%m-%d')
    attendance_records = [r for r in current_app.data_manager.data['attendance'] if r['date'] == today]
    employees = current_app.data_manager.get_all_users(role='employee')
    
    # Generate daily OTP
    daily_otp = current_app.data_manager.generate_daily_otp()
    
    context = {
        'attendance_records': attendance_records,
        'employees': employees,
        'today': today,
        'daily_otp': daily_otp
    }
    
    return render_template('manager/attendance.html', **context)

@manager_bp.route('/attendance/generate-otp', methods=['POST'])
@manager_required
def generate_otp():
    """Generate new daily OTP"""
    new_otp = current_app.data_manager.generate_daily_otp()
    flash(f'New OTP generated: {new_otp}', 'success')
    return redirect(url_for('manager.attendance'))

@manager_bp.route('/attendance/verify', methods=['POST'])
@manager_required
def verify_attendance():
    """Verify employee attendance with OTP"""
    employee_id = request.form.get('employee_id')
    otp = request.form.get('otp')
    action = request.form.get('action')  # check_in or check_out
    
    # Verify OTP against daily OTP
    if current_app.data_manager.verify_otp(otp):
        attendance_data = {
            'employee_id': employee_id,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'otp_used': otp,
            'location': 'Office'  # In real system, get from GPS
        }
        
        if action == 'check_in':
            attendance_data['check_in'] = datetime.now().strftime('%H:%M:%S')
        elif action == 'check_out':
            attendance_data['check_out'] = datetime.now().strftime('%H:%M:%S')
        
        current_app.data_manager.create_attendance_record(attendance_data)
        flash(f'Attendance {action} recorded successfully.', 'success')
    else:
        flash('Invalid OTP. Please try again.', 'error')
    
    return redirect(url_for('manager.attendance'))

@manager_bp.route('/tasks')
@manager_required
def tasks():
    """Task management page"""
    return render_template('manager/tasks.html')

@manager_bp.route('/inventory')
@manager_required
def inventory():
    """Inventory management page"""
    return render_template('manager/inventory.html')

@manager_bp.route('/reports')
@manager_required
def reports():
    """Team reports page"""
    return render_template('manager/reports.html')

@manager_bp.route('/analytics')
@manager_required
def analytics():
    """Team analytics page"""
    user_id = session.get('user_id')
    analytics_data = current_app.data_manager.get_analytics()
    
    # Get team-specific data
    employees = current_app.data_manager.get_all_users(role='employee')
    projects = current_app.data_manager.get_all_projects()
    clients = current_app.data_manager.get_all_clients()
    
    # Calculate team metrics
    total_team_projects = len(projects)
    active_team_projects = len([p for p in projects if p['status'] == 'in_progress'])
    completed_team_projects = len([p for p in projects if p['status'] == 'completed'])
    
    # Team performance by department
    department_stats = {}
    for employee in employees:
        dept = employee.get('department', 'General')
        if dept not in department_stats:
            department_stats[dept] = {'count': 0, 'projects': 0}
        department_stats[dept]['count'] += 1
    
    # Add project counts to departments
    for project in projects:
        for employee_id in project.get('assigned_employees', []):
            employee = current_app.data_manager.get_user_by_id(employee_id)
            if employee:
                dept = employee.get('department', 'General')
                if dept in department_stats:
                    department_stats[dept]['projects'] += 1
    
    context = {
        'analytics': analytics_data,
        'total_team_projects': total_team_projects,
        'active_team_projects': active_team_projects,
        'completed_team_projects': completed_team_projects,
        'total_employees': len(employees),
        'total_clients': len(clients),
        'department_stats': department_stats,
        'recent_projects': projects[-5:] if projects else []
    }
    
    return render_template('manager/analytics.html', **context)

@manager_bp.route('/api/team-analytics')
@manager_required
def api_team_analytics():
    """API endpoint for team analytics"""
    analytics = current_app.data_manager.get_analytics()
    return jsonify(analytics)
