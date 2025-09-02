# Firebase Data Manager for Trivanta Edge ERP
# Complete replacement for local JSON storage

import json
import os
from datetime import datetime, timedelta
import secrets
from typing import Dict, Any, Optional, List
import logging
from utils.security import security_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FirebaseDataManager:
    """Firebase-based data management for Trivanta Edge ERP with fallback to local storage"""
    
    def __init__(self):
        self.use_local_storage = True  # Fallback to local storage for now
        self.data_file = 'data/trivanta_erp.json'
        self.data = {}
        self.ensure_data_directory()
        self.load_data()
        
        # Try to initialize Firebase, but don't fail if it doesn't work
        try:
            from utils.firebase_config import get_firebase_data_manager
            self.firebase = get_firebase_data_manager()
            self.firebase.initialize()
            
            # Check if Firebase is actually working
            if self.check_firebase_status():
                self.firebase_ready = True
                self.use_local_storage = False
                logger.info("✅ Firebase initialized successfully, using cloud storage")
            else:
                self.firebase_ready = False
                self.use_local_storage = True
                logger.warning("⚠️ Firebase not ready, using local storage")
        except Exception as e:
            logger.warning(f"⚠️ Firebase initialization failed, using local storage: {e}")
            self.firebase_ready = False
            self.use_local_storage = True
    
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
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
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
        
    def ensure_admin_user(self):
        """Ensure admin user exists in the system"""
        try:
            admin_exists = any(user.get('role') == 'admin' for user in self.data.get('users', []))
            if not admin_exists:
                admin_user = {
                    "id": "admin_001",
                    "name": "Siddhant_MD",
                    "email": "admin@trivantaedge.com",
                    "password": security_manager.hash_password("As@102005"),
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
                logger.info("Admin user created successfully")
        except Exception as e:
            logger.error(f"Error ensuring admin user: {e}")
    
    def initialize_default_data(self):
        """Initialize system with fresh data - only admin user"""
        try:
            # Clear all existing data
            self.data = self.get_default_structure()
            
            # Create only admin user
            self.ensure_admin_user()
            
            self.save_data()
            logger.info("System initialized with fresh data")
            
        except Exception as e:
            logger.error(f"Error initializing default data: {e}")
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
        try:
            user_data['id'] = f"user_{len(self.data.get('users', [])) + 1:03d}"
            user_data['created_at'] = datetime.now().isoformat()
            user_data['status'] = 'active'
            user_data['api_key'] = security_manager.generate_api_key()
            
            if 'users' not in self.data:
                self.data['users'] = []
            self.data['users'].append(user_data)
            self.save_data()
            
            logger.info(f"User created: {user_data['name']}")
            return user_data
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            for user in self.data.get('users', []):
                if user.get('email') == email:
                    return user
            return None
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            for user in self.data.get('users', []):
                if user.get('id') == user_id:
                    return user
            return None
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
    
    def get_all_users(self, role: str = None) -> List[Dict[str, Any]]:
        """Get all users, optionally filtered by role"""
        try:
            users = self.data.get('users', [])
            if role:
                return [user for user in users if user.get('role') == role]
            return users
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """Update user"""
        try:
            for i, user in enumerate(self.data.get('users', [])):
                if user.get('id') == user_id:
                    self.data['users'][i].update(user_data)
                    self.save_data()
                    return True
            return False
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return False
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        try:
            for i, user in enumerate(self.data.get('users', [])):
                if user.get('id') == user_id:
                    del self.data['users'][i]
                    self.save_data()
                    return True
            return False
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with email and password"""
        try:
            user = self.get_user_by_email(email)
            if user and security_manager.verify_password(password, user['password']):
                return user
            return None
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None
    
    def create_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new client"""
        try:
            client_data['id'] = f"client_{len(self.data.get('clients', [])) + 1:03d}"
            client_data['created_at'] = datetime.now().isoformat()
            client_data['status'] = 'active'
            
            if 'clients' not in self.data:
                self.data['clients'] = []
            self.data['clients'].append(client_data)
            self.save_data()
            
            logger.info(f"Client created: {client_data['name']}")
            return client_data
            
        except Exception as e:
            logger.error(f"Error creating client: {e}")
            raise
    
    def get_all_clients(self) -> List[Dict[str, Any]]:
        """Get all clients"""
        try:
            return self.data.get('clients', [])
        except Exception as e:
            logger.error(f"Error getting all clients: {e}")
            return []
    
    def get_client_by_id(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get client by ID"""
        try:
            for client in self.data.get('clients', []):
                if client.get('id') == client_id:
                    return client
            return None
        except Exception as e:
            logger.error(f"Error getting client by ID: {e}")
            return None
    
    def update_client(self, client_id: str, client_data: Dict[str, Any]) -> bool:
        """Update client"""
        try:
            for i, client in enumerate(self.data.get('clients', [])):
                if client.get('id') == client_id:
                    self.data['clients'][i].update(client_data)
                    self.save_data()
                    return True
            return False
        except Exception as e:
            logger.error(f"Error updating client: {e}")
            return False
    
    def delete_client(self, client_id: str) -> bool:
        """Delete client"""
        try:
            for i, client in enumerate(self.data.get('clients', [])):
                if client.get('id') == client_id:
                    del self.data['clients'][i]
                    self.save_data()
                    return True
            return False
        except Exception as e:
            logger.error(f"Error deleting client: {e}")
            return False
    
    def create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project"""
        try:
            project_data['id'] = f"project_{len(self.data.get('projects', [])) + 1:03d}"
            project_data['created_at'] = datetime.now().isoformat()
            project_data['status'] = project_data.get('status', 'pending')
            project_data['progress'] = project_data.get('progress', 0)
            
            if 'projects' not in self.data:
                self.data['projects'] = []
            self.data['projects'].append(project_data)
            self.save_data()
            
            logger.info(f"Project created: {project_data['name']}")
            return project_data
            
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            raise
    
    def get_all_projects(self) -> List[Dict[str, Any]]:
        """Get all projects"""
        try:
            return self.data.get('projects', [])
        except Exception as e:
            logger.error(f"Error getting all projects: {e}")
            return []
    
    def get_project_by_id(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project by ID"""
        try:
            for project in self.data.get('projects', []):
                if project.get('id') == project_id:
                    return project
            return None
        except Exception as e:
            logger.error(f"Error getting project by ID: {e}")
            return None
    
    def update_project(self, project_id: str, project_data: Dict[str, Any]) -> bool:
        """Update project"""
        try:
            for i, project in enumerate(self.data.get('projects', [])):
                if project.get('id') == project_id:
                    self.data['projects'][i].update(project_data)
                    self.save_data()
                    return True
            return False
        except Exception as e:
            logger.error(f"Error updating project: {e}")
            return False
    
    def delete_project(self, project_id: str) -> bool:
        """Delete project"""
        try:
            for i, project in enumerate(self.data.get('projects', [])):
                if project.get('id') == project_id:
                    del self.data['projects'][i]
                    self.save_data()
                    return True
            return False
        except Exception as e:
            logger.error(f"Error deleting project: {e}")
            return False
    
    def get_projects_by_client(self, client_id: str) -> List[Dict[str, Any]]:
        """Get projects by client ID"""
        try:
            return [p for p in self.data.get('projects', []) if p.get('client_id') == client_id]
        except Exception as e:
            logger.error(f"Error getting projects by client: {e}")
            return []
    
    def create_employee(self, employee_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new employee"""
        try:
            employee_data['id'] = f"employee_{len(self.data.get('employees', [])) + 1:03d}"
            employee_data['created_at'] = datetime.now().isoformat()
            employee_data['status'] = 'active'
            
            if 'employees' not in self.data:
                self.data['employees'] = []
            self.data['employees'].append(employee_data)
            self.save_data()
            
            logger.info(f"Employee created: {employee_data['name']}")
            return employee_data
            
        except Exception as e:
            logger.error(f"Error creating employee: {e}")
            raise
    
    def get_all_employees(self) -> List[Dict[str, Any]]:
        """Get all employees"""
        try:
            return self.data.get('employees', [])
        except Exception as e:
            logger.error(f"Error getting all employees: {e}")
            return []
    
    def get_employee_by_id(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """Get employee by ID"""
        try:
            for employee in self.data.get('employees', []):
                if employee.get('id') == employee_id:
                    return employee
            return None
        except Exception as e:
            logger.error(f"Error getting employee by ID: {e}")
            return None
    
    def update_employee(self, employee_id: str, employee_data: Dict[str, Any]) -> bool:
        """Update employee"""
        try:
            for i, employee in enumerate(self.data.get('employees', [])):
                if employee.get('id') == employee_id:
                    self.data['employees'][i].update(employee_data)
                    self.save_data()
                    return True
            return False
        except Exception as e:
            logger.error(f"Error updating employee: {e}")
            return False
    
    def delete_employee(self, employee_id: str) -> bool:
        """Delete employee"""
        try:
            for i, employee in enumerate(self.data.get('employees', [])):
                if employee.get('id') == employee_id:
                    del self.data['employees'][i]
                    self.save_data()
                    return True
            return False
        except Exception as e:
            logger.error(f"Error deleting employee: {e}")
            return False
    
    def create_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new lead"""
        try:
            lead_data['id'] = f"lead_{len(self.data.get('leads', [])) + 1:03d}"
            lead_data['created_at'] = datetime.now().isoformat()
            lead_data['status'] = lead_data.get('status', 'new')
            
            if 'leads' not in self.data:
                self.data['leads'] = []
            self.data['leads'].append(lead_data)
            self.save_data()
            
            logger.info(f"Lead created: {lead_data['name']}")
            return lead_data
            
        except Exception as e:
            logger.error(f"Error creating lead: {e}")
            raise
    
    def get_all_leads(self) -> List[Dict[str, Any]]:
        """Get all leads"""
        try:
            return self.data.get('leads', [])
        except Exception as e:
            logger.error(f"Error getting all leads: {e}")
            return []
    
    def get_lead_by_id(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """Get lead by ID"""
        try:
            for lead in self.data.get('leads', []):
                if lead.get('id') == lead_id:
                    return lead
            return None
        except Exception as e:
            logger.error(f"Error getting lead by ID: {e}")
            return None
    
    def update_lead(self, lead_id: str, lead_data: Dict[str, Any]) -> bool:
        """Update lead"""
        try:
            for i, lead in enumerate(self.data.get('leads', [])):
                if lead.get('id') == lead_id:
                    self.data['leads'][i].update(lead_data)
                    self.save_data()
                    return True
            return False
        except Exception as e:
            logger.error(f"Error updating lead: {e}")
            return False
    
    def delete_lead(self, lead_id: str) -> bool:
        """Delete lead"""
        try:
            for i, lead in enumerate(self.data.get('leads', [])):
                if lead.get('id') == lead_id:
                    del self.data['leads'][i]
                    self.save_data()
                    return True
            return False
        except Exception as e:
            logger.error(f"Error deleting lead: {e}")
            return False
    
    def create_attendance_record(self, attendance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create attendance record"""
        try:
            attendance_data['id'] = f"attendance_{len(self.data.get('attendance', [])) + 1:03d}"
            attendance_data['created_at'] = datetime.now().isoformat()
            
            if 'attendance' not in self.data:
                self.data['attendance'] = []
            self.data['attendance'].append(attendance_data)
            self.save_data()
            
            logger.info(f"Attendance record created for {attendance_data.get('employee_name', 'Unknown')}")
            return attendance_data
            
        except Exception as e:
            logger.error(f"Error creating attendance: {e}")
            raise
    
    def get_attendance_by_employee(self, employee_id: str, date: str = None) -> List[Dict[str, Any]]:
        """Get attendance records for an employee"""
        try:
            attendance_records = []
            for record in self.data.get('attendance', []):
                if record.get('employee_id') == employee_id:
                    if not date or record.get('date') == date:
                        attendance_records.append(record)
            return attendance_records
        except Exception as e:
            logger.error(f"Error getting attendance: {e}")
            return []
    
    def get_all_attendance(self) -> List[Dict[str, Any]]:
        """Get all attendance records"""
        try:
            return self.data.get('attendance', [])
        except Exception as e:
            logger.error(f"Error getting all attendance: {e}")
            return []
    
    def get_attendance_by_date(self, date: str, department: str = None) -> List[Dict[str, Any]]:
        """Get attendance records for a specific date"""
        try:
            attendance_records = []
            for record in self.data.get('attendance', []):
                if record.get('date') == date:
                    if department:
                        # Get employee department
                        employee = self.get_user_by_id(record.get('employee_id'))
                        if employee and employee.get('department') == department:
                            attendance_records.append(record)
                    else:
                        attendance_records.append(record)
            
            # Add employee names to attendance records
            for record in attendance_records:
                if record.get('employee_id'):
                    employee = self.get_user_by_id(record['employee_id'])
                    if employee:
                        record['employee_name'] = employee['name']
                        record['department'] = employee.get('department', 'Unknown')
            
            return attendance_records
        except Exception as e:
            logger.error(f"Error getting attendance by date: {e}")
            return []
    
    def get_attendance_by_id(self, attendance_id: str) -> Optional[Dict[str, Any]]:
        """Get attendance record by ID"""
        try:
            for record in self.data.get('attendance', []):
                if record.get('id') == attendance_id:
                    return record
            return None
        except Exception as e:
            logger.error(f"Error getting attendance by ID: {e}")
            return None
    
    def update_attendance(self, attendance_id: str, attendance_data: Dict[str, Any]) -> bool:
        """Update attendance record"""
        try:
            for i, record in enumerate(self.data.get('attendance', [])):
                if record.get('id') == attendance_id:
                    self.data['attendance'][i].update(attendance_data)
                    self.save_data()
                    return True
            return False
        except Exception as e:
            logger.error(f"Error updating attendance: {e}")
            return False
    
    def delete_attendance(self, attendance_id: str) -> bool:
        """Delete attendance record"""
        try:
            for i, record in enumerate(self.data.get('attendance', [])):
                if record.get('id') == attendance_id:
                    del self.data['attendance'][i]
                    self.save_data()
                    return True
            return False
        except Exception as e:
            logger.error(f"Error deleting attendance: {e}")
            return False
    
    def mark_attendance_present(self, attendance_id: str) -> bool:
        """Mark employee as present"""
        try:
            updates = {
                'status': 'present',
                'check_in': datetime.now().strftime('%H:%M:%S'),
                'updated_at': datetime.now().isoformat()
            }
            return self.update_attendance(attendance_id, updates)
        except Exception as e:
            logger.error(f"Error marking attendance present: {e}")
            return False
    
    def get_daily_otp(self) -> str:
        """Get daily OTP for attendance"""
        try:
            return self.data.get('daily_otp', '123456')
        except Exception as e:
            logger.error(f"Error getting daily OTP: {e}")
            return "000000"
    
    def set_daily_otp(self, otp: str) -> bool:
        """Set daily OTP for attendance"""
        try:
            self.data['daily_otp'] = otp
            self.save_data()
            logger.info(f"Daily OTP set to: {otp}")
            return True
        except Exception as e:
            logger.error(f"Error setting daily OTP: {e}")
            return False
    
    def generate_daily_otp(self) -> str:
        """Generate a new daily OTP"""
        try:
            otp = str(secrets.randbelow(900000) + 100000)  # 6-digit OTP
            self.set_daily_otp(otp)
            return otp
        except Exception as e:
            logger.error(f"Error generating daily OTP: {e}")
            return "123456"
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get system analytics"""
        try:
            return self.data.get('analytics', {
                'installation_revenue': 0,
                'manufacturing_revenue': 0,
                'total_projects': 0,
                'active_employees': 0
            })
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {
                'installation_revenue': 0,
                'manufacturing_revenue': 0,
                'total_projects': 0,
                'active_employees': 0
            }
    
    def update_analytics(self, analytics_data: Dict[str, Any]) -> bool:
        """Update system analytics"""
        try:
            self.data['analytics'] = analytics_data
            self.save_data()
            return True
        except Exception as e:
            logger.error(f"Error updating analytics: {e}")
            return False
    
    def save_data(self):
        """Save data to local file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2, default=str)
            logger.info("Data saved to local file")
            return True
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            return False
    
    def load_data(self):
        """Load data from local file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    self.data = json.load(f)
                logger.info("Data loaded from local file")
            else:
                self.data = self.get_default_structure()
                self.save_data()
            return True
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return False
    
    def force_reinitialize(self):
        """Force reinitialize with fresh data"""
        try:
            self.initialize_default_data()
            logger.info("Data reinitialized with fresh data")
            return True
        except Exception as e:
            logger.error(f"Error reinitializing data: {e}")
            return False
