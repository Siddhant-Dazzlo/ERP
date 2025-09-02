from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, current_app
from utils.auth import admin_required
from utils.security import SecurityManager
from datetime import datetime, timedelta
import csv
from io import StringIO

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with system overview"""
    try:
        analytics = current_app.data_manager.get_analytics()
    except:
        analytics = {}
    
    try:
        users = current_app.data_manager.get_all_users()
    except:
        users = []
    
    try:
        projects = current_app.data_manager.get_all_projects()
    except:
        projects = []
    
    try:
        clients = current_app.data_manager.get_all_clients()
    except:
        clients = []
    
    # Calculate revenue metrics
    installation_revenue = sum(p.get('budget', 0) for p in projects if p.get('type') == 'installation')
    manufacturing_revenue = sum(p.get('budget', 0) for p in projects if p.get('type') == 'manufacturing')
    
    # Get recent activities (mock data for now)
    recent_activities = [
        {
            'title': 'System Login',
            'description': 'Admin user logged in',
            'user': 'System Administrator',
            'time': datetime.now().strftime('%H:%M'),
            'status': 'Completed',
            'status_color': 'success',
            'icon': 'person-check'
        }
    ]
    
    context = {
        'analytics': analytics,
        'total_users': len(users),
        'total_projects': len(projects),
        'total_clients': len(clients),
        'installation_revenue': installation_revenue,
        'manufacturing_revenue': manufacturing_revenue,
        'recent_projects': projects[-5:] if projects else [],
        'recent_clients': clients[-5:] if clients else [],
        'recent_activities': recent_activities
    }
    
    return render_template('admin/dashboard.html', **context)

@admin_bp.route('/users')
@admin_required
def users():
    """User management page"""
    users = current_app.data_manager.get_all_users()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/create', methods=['GET', 'POST'])
@admin_required
def create_user():
    """Create new user"""
    if request.method == 'POST':
        # Initialize security manager
        security_manager = SecurityManager()
        
        user_data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'password': security_manager.hash_password(request.form.get('password')),  # Hash the password
            'role': request.form.get('role'),
            'department': request.form.get('department')
        }
        
        # Check if email already exists (check by email only, not by authentication)
        existing_user = None
        for user in current_app.data_manager.get_all_users():
            if user['email'] == user_data['email']:
                existing_user = user
                break
                
        if existing_user:
            flash('User with this email already exists.', 'error')
        else:
            new_user = current_app.data_manager.create_user(user_data)
            flash(f'User {new_user["name"]} created successfully.', 'success')
            return redirect(url_for('admin.users'))
    
    return render_template('admin/create_user.html')

@admin_bp.route('/users/<user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    """Edit existing user"""
    user = current_app.data_manager.get_user_by_id(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin.users'))
    
    if request.method == 'POST':
        # Initialize security manager
        security_manager = SecurityManager()
        
        updates = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'role': request.form.get('role'),
            'department': request.form.get('department')
        }
        
        if request.form.get('password'):
            updates['password'] = security_manager.hash_password(request.form.get('password'))  # Hash the password
        
        updated_user = current_app.data_manager.update_user(user_id, updates)
        if updated_user:
            flash('User updated successfully.', 'success')
            return redirect(url_for('admin.users'))
    
    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/users/<user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete user"""
    if current_app.data_manager.delete_user(user_id):
        flash('User deleted successfully.', 'success')
    else:
        flash('Failed to delete user.', 'error')
    return redirect(url_for('admin.users'))

# ===== PROJECTS MANAGEMENT =====
@admin_bp.route('/projects')
@admin_required
def projects():
    """Project overview page"""
    projects = current_app.data_manager.get_all_projects()
    clients = current_app.data_manager.get_all_clients()
    
    # Add client names to projects for display
    for project in projects:
        client = current_app.data_manager.get_client_by_id(project.get('client_id'))
        project['client_name'] = client['name'] if client else 'N/A'
    
    return render_template('admin/projects.html', projects=projects, clients=clients)

@admin_bp.route('/projects/create', methods=['POST'])
@admin_required
def create_project():
    """Create new project"""
    project_data = {
        'name': request.form.get('name'),
        'type': request.form.get('type'),
        'client_id': request.form.get('client_id'),
        'description': request.form.get('description'),
        'start_date': request.form.get('start_date'),
        'end_date': request.form.get('end_date'),
        'budget': float(request.form.get('budget', 0)),
        'created_by': session.get('user_id')
    }
    
    new_project = current_app.data_manager.create_project(project_data)
    if new_project:
        flash(f'Project {new_project["name"]} created successfully.', 'success')
    else:
        flash('Failed to create project.', 'error')
    
    return redirect(url_for('admin.projects'))

@admin_bp.route('/projects/<project_id>/edit', methods=['POST'])
@admin_required
def edit_project(project_id):
    """Edit existing project"""
    updates = {
        'name': request.form.get('name'),
        'status': request.form.get('status'),
        'budget': float(request.form.get('budget', 0)),
        'end_date': request.form.get('end_date'),
        'description': request.form.get('description')
    }
    
    updated_project = current_app.data_manager.update_project(project_id, updates)
    if updated_project:
        flash('Project updated successfully.', 'success')
    else:
        flash('Failed to update project.', 'error')
    
    return redirect(url_for('admin.projects'))

@admin_bp.route('/projects/<project_id>/delete', methods=['POST'])
@admin_required
def delete_project(project_id):
    """Delete project"""
    if current_app.data_manager.delete_project(project_id):
        flash('Project deleted successfully.', 'success')
    else:
        flash('Failed to delete project.', 'error')
    return redirect(url_for('admin.projects'))

# ===== CLIENTS MANAGEMENT =====
@admin_bp.route('/clients')
@admin_required
def clients():
    """Client overview page"""
    clients = current_app.data_manager.get_all_clients()
    return render_template('admin/clients.html', clients=clients)

@admin_bp.route('/clients/create', methods=['POST'])
@admin_required
def create_client():
    """Create new client"""
    client_data = {
        'name': request.form.get('name'),
        'email': request.form.get('email'),
        'phone': request.form.get('phone'),
        'company': request.form.get('company'),
        'business_type': request.form.get('business_type'),
        'address': request.form.get('address')
    }
    
    new_client = current_app.data_manager.create_client(client_data)
    if new_client:
        flash(f'Client {new_client["name"]} created successfully.', 'success')
    else:
        flash('Failed to create client.', 'error')
    
    return redirect(url_for('admin.clients'))

@admin_bp.route('/clients/<client_id>/edit', methods=['POST'])
@admin_required
def edit_client(client_id):
    """Edit existing client"""
    updates = {
        'name': request.form.get('name'),
        'email': request.form.get('email'),
        'phone': request.form.get('phone'),
        'company': request.form.get('company'),
        'business_type': request.form.get('business_type'),
        'address': request.form.get('address'),
        'status': request.form.get('status')
    }
    
    updated_client = current_app.data_manager.update_client(client_id, updates)
    if updated_client:
        flash('Client updated successfully.', 'success')
    else:
        flash('Failed to update client.', 'error')
    
    return redirect(url_for('admin.clients'))

@admin_bp.route('/clients/<client_id>/delete', methods=['POST'])
@admin_required
def delete_client(client_id):
    """Delete client"""
    if current_app.data_manager.delete_client(client_id):
        flash('Client deleted successfully.', 'success')
    else:
        flash('Failed to delete client.', 'error')
    return redirect(url_for('admin.clients'))

# ===== LEADS MANAGEMENT =====
@admin_bp.route('/leads')
@admin_required
def leads():
    """Leads overview page"""
    leads = current_app.data_manager.get_all_leads()
    employees = current_app.data_manager.get_all_users(role='employee')
    
    # Add employee names to leads for display
    for lead in leads:
        if lead.get('assigned_to'):
            employee = current_app.data_manager.get_user_by_id(lead['assigned_to'])
            lead['assigned_to_name'] = employee['name'] if employee else 'N/A'
        else:
            lead['assigned_to_name'] = 'Unassigned'
    
    return render_template('admin/leads.html', leads=leads, employees=employees)

@admin_bp.route('/leads/create', methods=['POST'])
@admin_required
def create_lead():
    """Create new lead"""
    lead_data = {
        'name': request.form.get('name'),
        'email': request.form.get('email'),
        'phone': request.form.get('phone'),
        'company': request.form.get('company'),
        'business_type': request.form.get('business_type'),
        'source': request.form.get('source'),
        'assigned_to': request.form.get('assigned_to'),
        'status': request.form.get('status'),
        'notes': request.form.get('notes'),
        'created_by': session.get('user_id')
    }
    
    new_lead = current_app.data_manager.create_lead(lead_data)
    if new_lead:
        flash(f'Lead {new_lead["name"]} created successfully.', 'success')
    else:
        flash('Failed to create lead.', 'error')
    
    return redirect(url_for('admin.leads'))

@admin_bp.route('/leads/<lead_id>/edit', methods=['POST'])
@admin_required
def edit_lead(lead_id):
    """Edit existing lead"""
    updates = {
        'name': request.form.get('name'),
        'email': request.form.get('email'),
        'phone': request.form.get('phone'),
        'company': request.form.get('company'),
        'business_type': request.form.get('business_type'),
        'source': request.form.get('source'),
        'assigned_to': request.form.get('assigned_to'),
        'status': request.form.get('status'),
        'notes': request.form.get('notes')
    }
    
    updated_lead = current_app.data_manager.update_lead(lead_id, updates)
    if updated_lead:
        flash('Lead updated successfully.', 'success')
    else:
        flash('Failed to update lead.', 'error')
    
    return redirect(url_for('admin.leads'))

@admin_bp.route('/leads/<lead_id>/convert', methods=['POST'])
@admin_required
def convert_lead(lead_id):
    """Convert lead to client and project"""
    lead = current_app.data_manager.get_lead_by_id(lead_id)
    if not lead:
        flash('Lead not found.', 'error')
        return redirect(url_for('admin.leads'))
    
    # Create client from lead
    client_data = {
        'name': request.form.get('client_name'),
        'email': lead.get('email', ''),
        'phone': lead.get('phone', ''),
        'company': request.form.get('company'),
        'business_type': lead.get('business_type'),
        'address': ''
    }
    
    new_client = current_app.data_manager.create_client(client_data)
    if not new_client:
        flash('Failed to create client.', 'error')
        return redirect(url_for('admin.leads'))
    
    # Create project from lead
    project_data = {
        'name': request.form.get('project_name'),
        'type': request.form.get('project_type'),
        'client_id': new_client['id'],
        'description': request.form.get('description'),
        'start_date': request.form.get('start_date'),
        'budget': float(request.form.get('budget', 0)),
        'created_by': session.get('user_id')
    }
    
    new_project = current_app.data_manager.create_project(project_data)
    if not new_project:
        flash('Failed to create project.', 'error')
        return redirect(url_for('admin.leads'))
    
    # Update lead status to converted
    current_app.data_manager.update_lead(lead_id, {'status': 'converted'})
    
    flash(f'Lead converted successfully! Client and project created.', 'success')
    return redirect(url_for('admin.leads'))

@admin_bp.route('/leads/<lead_id>/delete', methods=['POST'])
@admin_required
def delete_lead(lead_id):
    """Delete lead"""
    if current_app.data_manager.delete_lead(lead_id):
        flash('Lead deleted successfully.', 'success')
    else:
        flash('Failed to delete lead.', 'error')
    return redirect(url_for('admin.leads'))

# ===== ATTENDANCE MANAGEMENT =====
@admin_bp.route('/attendance')
@admin_required
def attendance():
    """Attendance overview page"""
    selected_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    department = request.args.get('department', '')
    
    # Get attendance records for selected date
    attendance_records = current_app.data_manager.get_attendance_by_date(selected_date, department)
    today_attendance = current_app.data_manager.get_attendance_by_date(datetime.now().strftime('%Y-%m-%d'))
    total_employees = len(current_app.data_manager.get_all_users(role='employee'))
    daily_otp = current_app.data_manager.get_daily_otp()
    
    context = {
        'attendance_records': attendance_records,
        'today_attendance': today_attendance,
        'total_employees': total_employees,
        'daily_otp': daily_otp,
        'selected_date': selected_date,
        'today_date': datetime.now().strftime('%Y-%m-%d')
    }
    
    return render_template('admin/attendance.html', **context)

@admin_bp.route('/attendance/bulk', methods=['POST'])
@admin_required
def bulk_attendance():
    """Handle bulk attendance operations"""
    action = request.form.get('action')
    employee_ids = request.form.getlist('employee_ids')
    
    if action == 'mark_present':
        for employee_id in employee_ids:
            # Check if attendance record exists for today
            today = datetime.now().strftime('%Y-%m-%d')
            existing_record = None
            for record in current_app.data_manager.data['attendance']:
                if record['employee_id'] == employee_id and record['date'] == today:
                    existing_record = record
                    break
            
            if not existing_record:
                # Create new attendance record
                attendance_data = {
                    'employee_id': employee_id,
                    'date': today,
                    'status': 'present',
                    'check_in': datetime.now().strftime('%H:%M:%S')
                }
                current_app.data_manager.create_attendance_record(attendance_data)
            else:
                # Update existing record
                existing_record['status'] = 'present'
                existing_record['updated_at'] = datetime.now().isoformat()
        
        flash(f'Marked {len(employee_ids)} employees as present.', 'success')
    
    elif action == 'mark_absent':
        for employee_id in employee_ids:
            # Check if attendance record exists for today
            today = datetime.now().strftime('%Y-%m-%d')
            existing_record = None
            for record in current_app.data_manager.data['attendance']:
                if record['employee_id'] == employee_id and record['date'] == today:
                    existing_record = record
                    break
            
            if not existing_record:
                # Create new attendance record
                attendance_data = {
                    'employee_id': employee_id,
                    'date': today,
                    'status': 'absent'
                }
                current_app.data_manager.create_attendance_record(attendance_data)
            else:
                # Update existing record
                existing_record['status'] = 'absent'
                existing_record['updated_at'] = datetime.now().isoformat()
        
        flash(f'Marked {len(employee_ids)} employees as absent.', 'success')
    
    current_app.data_manager.save_data()
    return redirect(url_for('admin.attendance'))

@admin_bp.route('/attendance/<attendance_id>/edit', methods=['POST'])
@admin_required
def edit_attendance(attendance_id):
    """Edit attendance record"""
    updates = {
        'date': request.form.get('date'),
        'check_in': request.form.get('check_in'),
        'check_out': request.form.get('check_out'),
        'status': request.form.get('status'),
        'otp_used': request.form.get('otp_used'),
        'location': request.form.get('location'),
        'notes': request.form.get('notes')
    }
    
    updated_attendance = current_app.data_manager.update_attendance(attendance_id, updates)
    if updated_attendance:
        flash('Attendance record updated successfully.', 'success')
    else:
        flash('Failed to update attendance record.', 'error')
    
    return redirect(url_for('admin.attendance'))

@admin_bp.route('/attendance/<attendance_id>/mark-present', methods=['POST'])
@admin_required
def mark_present(attendance_id):
    """Mark employee as present"""
    if current_app.data_manager.mark_attendance_present(attendance_id):
        flash('Employee marked as present.', 'success')
    else:
        flash('Failed to update attendance.', 'error')
    
    return redirect(url_for('admin.attendance'))

@admin_bp.route('/attendance/export')
@admin_required
def export_attendance():
    """Export attendance report to CSV"""
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    department = request.args.get('department', '')
    
    attendance_records = current_app.data_manager.get_attendance_by_date(date, department)
    
    # Create CSV
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Employee ID', 'Name', 'Department', 'Date', 'Check In', 'Check Out', 'Status', 'OTP Used', 'Location'])
    
    for record in attendance_records:
        cw.writerow([
            record.get('employee_id', ''),
            record.get('employee_name', ''),
            record.get('department', ''),
            record.get('date', ''),
            record.get('check_in', ''),
            record.get('check_out', ''),
            record.get('status', ''),
            record.get('otp_used', ''),
            record.get('location', '')
        ])
    
    output = si.getvalue()
    si.close()
    
    from flask import Response
    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=attendance_{date}.csv'}
    )

@admin_bp.route('/analytics')
@admin_required
def analytics():
    """Detailed analytics page"""
    analytics_data = current_app.data_manager.get_analytics()
    projects = current_app.data_manager.get_all_projects()
    clients = current_app.data_manager.get_all_clients()
    
    # Business type breakdown
    installation_clients = len([c for c in clients if c['business_type'] == 'installation'])
    manufacturing_clients = len([c for c in clients if c['business_type'] == 'manufacturing'])
    both_clients = len([c for c in clients if c['business_type'] == 'both'])
    
    # Project status breakdown
    project_statuses = {}
    for project in projects:
        status = project.get('status', 'unknown')
        project_statuses[status] = project_statuses.get(status, 0) + 1
    
    context = {
        'analytics': analytics_data,
        'installation_clients': installation_clients,
        'manufacturing_clients': manufacturing_clients,
        'both_clients': both_clients,
        'project_statuses': project_statuses,
        'total_revenue': sum(p.get('budget', 0) for p in projects)
    }
    
    return render_template('admin/analytics.html', **context)

@admin_bp.route('/reports')
@admin_required
def reports():
    """Reports generation page"""
    # Get analytics data for the reports page
    analytics = current_app.data_manager.get_analytics()
    projects = current_app.data_manager.get_all_projects()
    
    # Get top projects by budget
    top_projects = sorted(projects, key=lambda x: x.get('budget', 0), reverse=True)[:10]
    
    # Add client names to projects for display
    for project in top_projects:
        client = current_app.data_manager.get_client_by_id(project.get('client_id'))
        project['client_name'] = client['name'] if client else 'N/A'
        # Add mock progress for demonstration
        project['progress'] = 75 if project['status'] == 'in_progress' else (100 if project['status'] == 'completed' else 25)
    
    context = {
        'total_revenue': analytics.get('total_revenue', 0),
        'active_projects': len([p for p in projects if p['status'] == 'in_progress']),
        'conversion_rate': analytics.get('conversion_rate', 0),
        'attendance_rate': analytics.get('attendance_rate', 0),
        'top_projects': top_projects
    }
    
    return render_template('admin/reports.html', **context)

@admin_bp.route('/tasks')
@admin_required
def tasks():
    """Admin tasks management page"""
    projects = current_app.data_manager.get_all_projects()
    
    # Convert projects to tasks format for admin view
    tasks = []
    for project in projects:
        tasks.append({
            'id': project['id'],
            'name': project['name'],
            'type': project['type'],
            'status': project['status'],
            'client_id': project.get('client_id'),
            'assigned_employees': project.get('assigned_employees', []),
            'start_date': project.get('start_date', ''),
            'end_date': project.get('end_date', ''),
            'description': project.get('description', ''),
            'budget': project.get('budget', 0)
        })
    
    return render_template('admin/tasks.html', tasks=tasks)

@admin_bp.route('/settings')
@admin_required
def settings():
    """System settings page"""
    return render_template('admin/settings.html')

# ===== API ENDPOINTS =====
@admin_bp.route('/api/users')
@admin_required
def api_users():
    """API endpoint for users data"""
    users = current_app.data_manager.get_all_users()
    return jsonify(users)

@admin_bp.route('/api/analytics')
@admin_required
def api_analytics():
    """API endpoint for analytics data"""
    analytics = current_app.data_manager.get_analytics()
    return jsonify(analytics)

@admin_bp.route('/api/projects/<project_id>')
@admin_required
def api_project(project_id):
    """API endpoint for project data"""
    project = current_app.data_manager.get_project_by_id(project_id)
    if project:
        return jsonify(project)
    return jsonify({'error': 'Project not found'}), 404

@admin_bp.route('/api/clients/<client_id>')
@admin_required
def api_client(client_id):
    """API endpoint for client data"""
    client = current_app.data_manager.get_client_by_id(client_id)
    if client:
        return jsonify(client)
    return jsonify({'error': 'Client not found'}), 404

@admin_bp.route('/api/clients/<client_id>/projects')
@admin_required
def api_client_projects(client_id):
    """API endpoint for client projects"""
    client = current_app.data_manager.get_client_by_id(client_id)
    projects = current_app.data_manager.get_projects_by_client(client_id)
    
    return jsonify({
        'client_name': client['name'] if client else 'Unknown',
        'projects': projects
    })

@admin_bp.route('/api/leads/<lead_id>')
@admin_required
def api_lead(lead_id):
    """API endpoint for lead data"""
    lead = current_app.data_manager.get_lead_by_id(lead_id)
    if lead:
        return jsonify(lead)
    return jsonify({'error': 'Lead not found'}), 404

@admin_bp.route('/api/attendance/<attendance_id>')
@admin_required
def api_attendance(attendance_id):
    """API endpoint for attendance data"""
    attendance = current_app.data_manager.get_attendance_by_id(attendance_id)
    if attendance:
        return jsonify(attendance)
    return jsonify({'error': 'Attendance record not found'}), 404

@admin_bp.route('/api/employees')
@admin_required
def api_employees():
    """API endpoint for employees data"""
    employees = current_app.data_manager.get_all_users(role='employee')
    return jsonify(employees)

@admin_bp.route('/api/generate-otp', methods=['POST'])
@admin_required
def api_generate_otp():
    """API endpoint to generate daily OTP"""
    otp = current_app.data_manager.generate_daily_otp()
    current_app.data_manager.set_daily_otp(otp)
    return jsonify({'otp': otp})

