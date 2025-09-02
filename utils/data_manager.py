import json
import os
from datetime import datetime, timedelta
import secrets
from utils.security import security_manager

class DataManager:
    def __init__(self):
        self.data_file = 'data/trivanta_erp.json'
        self.ensure_data_directory()
        self.load_data()
    
    def ensure_data_directory(self):
        """Ensure the data directory exists"""
        os.makedirs('data', exist_ok=True)
    
    def load_data(self):
        """Load data from JSON file or create default structure"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.data = json.load(f)
            except:
                self.data = self.get_default_structure()
        else:
            self.data = self.get_default_structure()
            self.save_data()
    
    def save_data(self):
        """Save data to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2, default=str)
    
    def get_default_structure(self):
        """Get default data structure for Trivanta Edge ERP"""
        return {
            "users": [],
            "clients": [],
            "projects": [],
            "employees": [],
            "attendance": [],
            "leads": [],
            "tasks": [],
            "daily_otp": "",
            "analytics": {
                "installation_revenue": 0,
                "manufacturing_revenue": 0,
                "total_projects": 0,
                "active_employees": 0
            }
        }
    
    def force_reinitialize(self):
        """Force reinitialize with sample data (for testing)"""
        self.data = self.get_default_structure()
        self.initialize_default_data()
        self.save_data()
        print("Data reinitialized with sample data")
    
    def ensure_admin_user(self):
        """Ensure admin user exists in the system"""
        admin_exists = any(user.get('role') == 'admin' for user in self.data.get('users', []))
        if not admin_exists:
            admin_user = {
                "id": "admin_001",
                "name": "System Administrator",
                "email": "admin@trivantaedge.com",
                "password": security_manager.hash_password("admin123"),
                "role": "admin",
                "department": "Administration",
                "created_at": datetime.now().isoformat(),
                "status": "active",
                "api_key": security_manager.generate_api_key()
            }
            if 'users' not in self.data:
                self.data['users'] = []
            self.data['users'].append(admin_user)
            self.save_data()
            print("Admin user created successfully")
    
    def initialize_default_data(self):
        """Initialize system with default data"""
        if not self.data['users']:
            # Add default manager and employee accounts with enhanced security
            default_users = [
                {
                    "id": "manager_001",
                    "name": "John Manager",
                    "email": "manager@trivantaedge.com",
                    "password": security_manager.hash_password("Manager@123"),
                    "role": "manager",
                    "department": "Operations",
                    "created_at": datetime.now().isoformat(),
                    "status": "active",
                    "api_key": security_manager.generate_api_key()
                },
                {
                    "id": "employee_001",
                    "name": "Sarah Employee",
                    "email": "employee@trivantaedge.com",
                    "password": security_manager.hash_password("Employee@123"),
                    "role": "employee",
                    "department": "Installation",
                    "created_at": datetime.now().isoformat(),
                    "status": "active",
                    "api_key": security_manager.generate_api_key()
                }
            ]
            self.data['users'].extend(default_users)
            
            # Add sample clients
            sample_clients = [
                {
                    "id": "client_001",
                    "name": "TechCorp Solutions",
                    "email": "contact@techcorp.com",
                    "phone": "+1-555-0123",
                    "company": "TechCorp Solutions Inc.",
                    "business_type": "installation",
                    "address": "123 Tech Street, Silicon Valley, CA",
                    "status": "active",
                    "created_at": datetime.now().isoformat()
                },
                {
                    "id": "client_002",
                    "name": "AutoPark Systems",
                    "email": "info@autopark.com",
                    "phone": "+1-555-0456",
                    "company": "AutoPark Systems Ltd.",
                    "business_type": "manufacturing",
                    "address": "456 Auto Avenue, Detroit, MI",
                    "status": "active",
                    "created_at": datetime.now().isoformat()
                }
            ]
            self.data['clients'].extend(sample_clients)
            
            # Add sample projects
            sample_projects = [
                {
                    "id": "project_001",
                    "name": "TechCorp Parking Automation",
                    "type": "installation",
                    "client_id": "client_001",
                    "description": "Complete parking automation system for TechCorp headquarters",
                    "start_date": "2024-01-15",
                    "end_date": "2024-06-30",
                    "status": "in_progress",
                    "progress": 65,
                    "assigned_employees": ["employee_001"],
                    "created_at": datetime.now().isoformat()
                },
                {
                    "id": "project_002",
                    "name": "AutoPark Stacker Manufacturing",
                    "type": "manufacturing",
                    "client_id": "client_002",
                    "description": "Manufacturing of 50 parking stackers for AutoPark",
                    "start_date": "2024-02-01",
                    "end_date": "2024-08-31",
                    "status": "pending",
                    "progress": 0,
                    "assigned_employees": [],
                    "created_at": datetime.now().isoformat()
                }
            ]
            self.data['projects'].extend(sample_projects)
            
            # Add sample leads
            sample_leads = [
                {
                    "id": "lead_001",
                    "name": "Mike Johnson",
                    "email": "mike@megacorp.com",
                    "phone": "+1-555-0789",
                    "company": "MegaCorp Industries",
                    "business_type": "both",
                    "source": "website",
                    "status": "new",
                    "priority": "high",
                    "assigned_to": "manager_001",
                    "notes": "Interested in both installation and manufacturing services",
                    "created_at": datetime.now().isoformat()
                },
                {
                    "id": "lead_002",
                    "name": "Lisa Chen",
                    "email": "lisa@startupco.com",
                    "phone": "+1-555-0321",
                    "company": "StartupCo",
                    "business_type": "installation",
                    "source": "referral",
                    "status": "contacted",
                    "priority": "medium",
                    "assigned_to": None,
                    "notes": "Small startup looking for affordable parking solution",
                    "created_at": datetime.now().isoformat()
                }
            ]
            self.data['leads'].extend(sample_leads)
            
            # Add sample attendance records
            sample_attendance = [
                {
                    "id": "att_001",
                    "employee_id": "employee_001",
                    "date": datetime.now().strftime('%Y-%m-%d'),
                    "check_in": "09:00:00",
                    "check_out": "17:00:00",
                    "status": "present",
                    "otp_used": "99598"
                }
            ]
            self.data['attendance'].extend(sample_attendance)
            
            # Generate initial daily OTP
            self.generate_daily_otp()
            
            self.save_data()
    
    # ===== USER MANAGEMENT =====
    def authenticate_user(self, email, password):
        """Authenticate user with email and password"""
        for user in self.data['users']:
            if user['email'] == email and user['status'] == 'active':
                # Use security manager to verify password
                if security_manager.verify_password(password, user['password']):
                    return user
        return None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        for user in self.data['users']:
            if user['id'] == user_id:
                return user
        return None
    
    def create_user(self, user_data):
        """Create new user"""
        user_id = f"{user_data['role']}_{len(self.data['users']) + 1:03d}"
        user = {
            "id": user_id,
            "name": user_data['name'],
            "email": user_data['email'],
            "password": user_data['password'],  # Should already be hashed
            "role": user_data['role'],
            "department": user_data.get('department', 'General'),
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "api_key": security_manager.generate_api_key()
        }
        self.data['users'].append(user)
        self.save_data()
        return user
    
    def update_user(self, user_id, updates):
        """Update user information"""
        user = self.get_user_by_id(user_id)
        if user:
            user.update(updates)
            user['updated_at'] = datetime.now().isoformat()
            self.save_data()
            return user
        return None
    
    def delete_user(self, user_id):
        """Delete user (soft delete)"""
        user = self.get_user_by_id(user_id)
        if user:
            user['status'] = 'inactive'
            user['deleted_at'] = datetime.now().isoformat()
            self.save_data()
            return True
        return False
    
    def get_all_users(self, role=None):
        """Get all users, optionally filtered by role"""
        if role:
            return [user for user in self.data['users'] if user['role'] == role and user['status'] == 'active']
        return [user for user in self.data['users'] if user['status'] == 'active']
    
    # ===== CLIENT MANAGEMENT =====
    def create_client(self, client_data):
        """Create new client"""
        client_id = f"client_{len(self.data['clients']) + 1:03d}"
        client = {
            "id": client_id,
            "name": client_data['name'],
            "email": client_data['email'],
            "phone": client_data.get('phone', ''),
            "company": client_data.get('company', ''),
            "business_type": client_data['business_type'],  # installation, manufacturing, both
            "address": client_data.get('address', ''),
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        self.data['clients'].append(client)
        self.save_data()
        return client
    
    def get_client_by_id(self, client_id):
        """Get client by ID"""
        for client in self.data['clients']:
            if client['id'] == client_id:
                return client
        return None
    
    def update_client(self, client_id, updates):
        """Update client information"""
        client = self.get_client_by_id(client_id)
        if client:
            client.update(updates)
            client['updated_at'] = datetime.now().isoformat()
            self.save_data()
            return client
        return None
    
    def delete_client(self, client_id):
        """Delete client (soft delete)"""
        client = self.get_client_by_id(client_id)
        if client:
            client['status'] = 'inactive'
            client['deleted_at'] = datetime.now().isoformat()
            self.save_data()
            return True
        return False
    
    def get_all_clients(self, business_type=None):
        """Get all clients, optionally filtered by business type"""
        if business_type:
            return [client for client in self.data['clients'] if client['business_type'] == business_type and client['status'] == 'active']
        return [client for client in self.data['clients'] if client['status'] == 'active']
    
    # ===== PROJECT MANAGEMENT =====
    def create_project(self, project_data):
        """Create new project (installation or manufacturing)"""
        project_id = f"project_{len(self.data['projects']) + 1:03d}"
        project = {
            "id": project_id,
            "name": project_data['name'],
            "type": project_data['type'],  # installation or manufacturing
            "client_id": project_data['client_id'],
            "description": project_data.get('description', ''),
            "status": "pending",
            "start_date": project_data.get('start_date', ''),
            "end_date": project_data.get('end_date', ''),
            "budget": project_data.get('budget', 0),
            "assigned_employees": project_data.get('assigned_employees', []),
            "created_at": datetime.now().isoformat(),
            "created_by": project_data['created_by']
        }
        self.data['projects'].append(project)
        self.save_data()
        return project
    
    def get_project_by_id(self, project_id):
        """Get project by ID"""
        for project in self.data['projects']:
            if project['id'] == project_id:
                return project
        return None
    
    def update_project(self, project_id, updates):
        """Update project information"""
        project = self.get_project_by_id(project_id)
        if project:
            project.update(updates)
            project['updated_at'] = datetime.now().isoformat()
            self.save_data()
            return project
        return None
    
    def delete_project(self, project_id):
        """Delete project (soft delete)"""
        project = self.get_project_by_id(project_id)
        if project:
            project['status'] = 'deleted'
            project['deleted_at'] = datetime.now().isoformat()
            self.save_data()
            return True
        return False
    
    def get_all_projects(self, project_type=None):
        """Get all projects, optionally filtered by type"""
        if project_type:
            return [project for project in self.data['projects'] if project['type'] == project_type and project.get('status') != 'deleted']
        return [project for project in self.data['projects'] if project.get('status') != 'deleted']
    
    def get_projects_by_client(self, client_id):
        """Get all projects for a specific client"""
        return [project for project in self.data['projects'] if project.get('client_id') == client_id and project.get('status') != 'deleted']
    
    # ===== LEAD MANAGEMENT =====
    def create_lead(self, lead_data):
        """Create new lead"""
        lead_id = f"lead_{len(self.data['leads']) + 1:03d}"
        lead = {
            "id": lead_id,
            "name": lead_data['name'],
            "email": lead_data.get('email', ''),
            "phone": lead_data.get('phone', ''),
            "company": lead_data.get('company', ''),
            "business_type": lead_data['business_type'],
            "source": lead_data.get('source', ''),
            "status": "new",
            "assigned_to": lead_data.get('assigned_to', ''),
            "notes": lead_data.get('notes', ''),
            "created_at": datetime.now().isoformat(),
            "created_by": lead_data['created_by']
        }
        self.data['leads'].append(lead)
        self.save_data()
        return lead
    
    def get_lead_by_id(self, lead_id):
        """Get lead by ID"""
        for lead in self.data['leads']:
            if lead['id'] == lead_id:
                return lead
        return None
    
    def update_lead(self, lead_id, updates):
        """Update lead information"""
        lead = self.get_lead_by_id(lead_id)
        if lead:
            lead.update(updates)
            lead['updated_at'] = datetime.now().isoformat()
            self.save_data()
            return lead
        return None
    
    def delete_lead(self, lead_id):
        """Delete lead (soft delete)"""
        lead = self.get_lead_by_id(lead_id)
        if lead:
            lead['status'] = 'deleted'
            lead['deleted_at'] = datetime.now().isoformat()
            self.save_data()
            return True
        return False
    
    def get_all_leads(self, business_type=None):
        """Get all leads, optionally filtered by business type"""
        if business_type:
            return [lead for lead in self.data['leads'] if lead['business_type'] == business_type and lead.get('status') != 'deleted']
        return [lead for lead in self.data['leads'] if lead.get('status') != 'deleted']
    
    # ===== ATTENDANCE MANAGEMENT =====
    def create_attendance_record(self, attendance_data):
        """Create attendance record with OTP verification"""
        attendance_id = f"attendance_{len(self.data['attendance']) + 1:03d}"
        attendance = {
            "id": attendance_id,
            "employee_id": attendance_data['employee_id'],
            "date": attendance_data['date'],
            "check_in": attendance_data.get('check_in', ''),
            "check_out": attendance_data.get('check_out', ''),
            "otp_used": attendance_data.get('otp_used', ''),
            "location": attendance_data.get('location', ''),
            "status": "present"
        }
        self.data['attendance'].append(attendance)
        self.save_data()
        return attendance
    
    def get_attendance_by_id(self, attendance_id):
        """Get attendance record by ID"""
        for record in self.data['attendance']:
            if record['id'] == attendance_id:
                # Add employee information
                employee = self.get_user_by_id(record['employee_id'])
                if employee:
                    record['employee_name'] = employee['name']
                    record['department'] = employee['department']
                return record
        return None
    
    def update_attendance(self, attendance_id, updates):
        """Update attendance record"""
        record = self.get_attendance_by_id(attendance_id)
        if record:
            record.update(updates)
            record['updated_at'] = datetime.now().isoformat()
            self.save_data()
            return record
        return None
    
    def mark_attendance_present(self, attendance_id):
        """Mark attendance as present"""
        record = self.get_attendance_by_id(attendance_id)
        if record:
            record['status'] = 'present'
            record['updated_at'] = datetime.now().isoformat()
            self.save_data()
            return True
        return False
    
    def delete_attendance(self, attendance_id):
        """Delete attendance record"""
        for i, record in enumerate(self.data['attendance']):
            if record['id'] == attendance_id:
                del self.data['attendance'][i]
                self.save_data()
                return True
        return False
    
    def get_attendance_by_date(self, date, department=None):
        """Get attendance records for a specific date"""
        records = []
        for record in self.data['attendance']:
            if record['date'] == date:
                # Add employee information
                employee = self.get_user_by_id(record['employee_id'])
                if employee:
                    record['employee_name'] = employee['name']
                    record['department'] = employee['department']
                    
                    # Filter by department if specified
                    if department and employee['department'] != department:
                        continue
                    
                    records.append(record)
        return records
    
    def get_attendance_by_employee(self, employee_id, start_date=None, end_date=None):
        """Get attendance records for a specific employee within date range"""
        records = []
        for record in self.data['attendance']:
            if record['employee_id'] == employee_id:
                if start_date and record['date'] < start_date:
                    continue
                if end_date and record['date'] > end_date:
                    continue
                records.append(record)
        return records
    
    # ===== OTP MANAGEMENT =====
    def generate_daily_otp(self):
        """Generate daily OTP for attendance"""
        otp = str(secrets.randbelow(100000)).zfill(5)
        self.set_daily_otp(otp)
        return otp
    
    def set_daily_otp(self, otp):
        """Set daily OTP"""
        self.data['daily_otp'] = otp
        self.data['daily_otp_date'] = datetime.now().strftime('%Y-%m-%d')
        self.save_data()
        return otp
    
    def get_daily_otp(self):
        """Get current daily OTP"""
        today = datetime.now().strftime('%Y-%m-%d')
        stored_date = self.data.get('daily_otp_date', '')
        
        # If OTP is from a different day, generate new one
        if stored_date != today:
            return self.generate_daily_otp()
        
        return self.data.get('daily_otp', '')
    
    def verify_otp(self, otp):
        """Verify if OTP is valid for today"""
        current_otp = self.get_daily_otp()
        return otp == current_otp
    
    # ===== ANALYTICS =====
    def get_analytics(self):
        """Get system analytics"""
        total_projects = len(self.data['projects'])
        active_employees = len([user for user in self.data['users'] if user['role'] == 'employee' and user['status'] == 'active'])
        
        installation_projects = len([p for p in self.data['projects'] if p['type'] == 'installation'])
        manufacturing_projects = len([p for p in self.data['projects'] if p['type'] == 'manufacturing'])
        
        # Calculate revenue
        total_revenue = sum(p.get('budget', 0) for p in self.data['projects'])
        installation_revenue = sum(p.get('budget', 0) for p in self.data['projects'] if p['type'] == 'installation')
        manufacturing_revenue = sum(p.get('budget', 0) for p in self.data['projects'] if p['type'] == 'manufacturing')
        
        # Lead conversion rate
        total_leads = len(self.data['leads'])
        converted_leads = len([l for l in self.data['leads'] if l['status'] == 'converted'])
        conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0
        
        # Attendance statistics
        today = datetime.now().strftime('%Y-%m-%d')
        today_attendance = self.get_attendance_by_date(today)
        attendance_rate = (len(today_attendance) / active_employees * 100) if active_employees > 0 else 0
        
        return {
            "total_projects": total_projects,
            "installation_projects": installation_projects,
            "manufacturing_projects": manufacturing_projects,
            "active_employees": active_employees,
            "total_clients": len(self.data['clients']),
            "total_leads": total_leads,
            "converted_leads": converted_leads,
            "conversion_rate": round(conversion_rate, 2),
            "total_revenue": total_revenue,
            "installation_revenue": installation_revenue,
            "manufacturing_revenue": manufacturing_revenue,
            "attendance_rate": round(attendance_rate, 2),
            "today_attendance": len(today_attendance)
        }
    
    # ===== BUSINESS PROCESS AUTOMATION =====
    def auto_assign_leads(self):
        """Automatically assign unassigned leads to available employees"""
        unassigned_leads = [lead for lead in self.data['leads'] if not lead.get('assigned_to') and lead['status'] == 'new']
        available_employees = [user for user in self.data['users'] if user['role'] == 'employee' and user['status'] == 'active']
        
        if not available_employees or not unassigned_leads:
            return
        
        # Simple round-robin assignment
        for i, lead in enumerate(unassigned_leads):
            employee = available_employees[i % len(available_employees)]
            lead['assigned_to'] = employee['id']
            lead['updated_at'] = datetime.now().isoformat()
        
        self.save_data()
    
    def auto_update_project_status(self):
        """Automatically update project statuses based on dates"""
        today = datetime.now().date()
        
        for project in self.data['projects']:
            if project['status'] in ['pending', 'in_progress']:
                start_date = datetime.strptime(project['start_date'], '%Y-%m-%d').date() if project['start_date'] else None
                end_date = datetime.strptime(project['end_date'], '%Y-%m-%d').date() if project['end_date'] else None
                
                if start_date and today >= start_date and project['status'] == 'pending':
                    project['status'] = 'in_progress'
                    project['updated_at'] = datetime.now().isoformat()
                
                if end_date and today >= end_date and project['status'] == 'in_progress':
                    project['status'] = 'completed'
                    project['updated_at'] = datetime.now().isoformat()
        
        self.save_data()
    
    def generate_daily_reports(self):
        """Generate daily reports for management"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Attendance report
        attendance_records = self.get_attendance_by_date(today)
        present_count = len([r for r in attendance_records if r['status'] == 'present'])
        absent_count = len([r for r in attendance_records if r['status'] == 'absent'])
        
        # Project updates
        active_projects = [p for p in self.data['projects'] if p['status'] == 'in_progress']
        
        # New leads
        new_leads = [l for l in self.data['leads'] if l['status'] == 'new']
        
        report = {
            'date': today,
            'attendance': {
                'present': present_count,
                'absent': absent_count,
                'total_employees': len(self.data['users'])
            },
            'projects': {
                'active': len(active_projects),
                'total': len(self.data['projects'])
            },
            'leads': {
                'new': len(new_leads),
                'total': len(self.data['leads'])
            }
        }
        
        return report
    
    # ===== TASK MANAGEMENT =====
    def create_task(self, task_data):
        """Create new task"""
        task_id = f"task_{len(self.data['tasks']) + 1:03d}"
        task = {
            "id": task_id,
            "title": task_data['title'],
            "description": task_data.get('description', ''),
            "project_id": task_data.get('project_id', ''),
            "assigned_to": task_data.get('assigned_to', ''),
            "priority": task_data.get('priority', 'medium'),
            "status": "pending",
            "due_date": task_data.get('due_date', ''),
            "created_at": datetime.now().isoformat(),
            "created_by": task_data['created_by']
        }
        self.data['tasks'].append(task)
        self.save_data()
        return task
    
    def get_task_by_id(self, task_id):
        """Get task by ID"""
        for task in self.data['tasks']:
            if task['id'] == task_id:
                return task
        return None
    
    def update_task(self, task_id, updates):
        """Update task information"""
        task = self.get_task_by_id(task_id)
        if task:
            task.update(updates)
            task['updated_at'] = datetime.now().isoformat()
            self.save_data()
            return task
        return None
    
    def delete_task(self, task_id):
        """Delete task"""
        for i, task in enumerate(self.data['tasks']):
            if task['id'] == task_id:
                del self.data['tasks'][i]
                self.save_data()
                return True
        return False
    
    def get_all_tasks(self, assigned_to=None, project_id=None, status=None):
        """Get all tasks, optionally filtered"""
        tasks = self.data['tasks']
        
        if assigned_to:
            tasks = [t for t in tasks if t.get('assigned_to') == assigned_to]
        if project_id:
            tasks = [t for t in tasks if t.get('project_id') == project_id]
        if status:
            tasks = [t for t in tasks if t.get('status') == status]
        
        return tasks
