from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'error')
                return redirect(url_for('login'))
            
            user_role = session.get('role')
            if user_role not in allowed_roles:
                flash('You do not have permission to access this page.', 'error')
                if user_role == 'admin':
                    return redirect(url_for('admin.dashboard'))
                elif user_role == 'manager':
                    return redirect(url_for('manager.dashboard'))
                elif user_role == 'employee':
                    return redirect(url_for('employee.dashboard'))
                else:
                    return redirect(url_for('login'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return role_required(['admin'])(f)

def manager_required(f):
    return role_required(['admin', 'manager'])(f)

def employee_required(f):
    return role_required(['admin', 'manager', 'employee'])(f)

