# 🔐 Trivanta ERP Test Credentials

## 📋 Login Information

### 👑 Admin Portal
- **Email**: `admin@trivantaedge.com`
- **Password**: `admin123`
- **Access**: Full system access

### 👔 Manager Portal  
- **Email**: `manager@trivantaedge.com`
- **Password**: `Manager@123`
- **Access**: Team management, projects, clients, leads

### 👷 Employee Portal
- **Email**: `employee@trivantaedge.com`
- **Password**: `Employee@123`
- **Access**: Personal dashboard, assigned projects, attendance

## 🚀 Quick Test Steps

1. **Start the Flask app**: `python app.py`
2. **Open browser**: Navigate to `http://127.0.0.1:8080`
3. **Test each portal** using the credentials above
4. **Check all pages** for errors and functionality

## ⚠️ Important Notes

- These are **TEST CREDENTIALS ONLY**
- Do not use in production
- Passwords are case-sensitive
- All portals should now work correctly

## 🔧 If Issues Persist

Run the password reset script:
```bash
python reset_passwords.py
```

## 📱 Test URLs

- **Admin**: `http://127.0.0.1:8080/admin/dashboard`
- **Manager**: `http://127.0.0.1:8080/manager/dashboard`  
- **Employee**: `http://127.0.0.1:8080/employee/dashboard`
