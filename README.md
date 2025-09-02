# Trivanta Edge ERP - Firebase Integration

A comprehensive Enterprise Resource Planning (ERP) system with Firebase integration for real-time data synchronization, cloud storage, and scalable architecture.

## 🚀 Features

- **Multi-Role Access**: Admin, Manager, and Employee portals
- **Real-Time Data Sync**: Firebase Firestore integration
- **Cloud Storage**: Firebase Storage for file management
- **Authentication**: Secure Firebase Auth with JWT tokens
- **Responsive UI**: Modern Bootstrap-based interface
- **Analytics**: Real-time dashboard with charts and metrics
- **Attendance Management**: OTP-based attendance system
- **Project Management**: Complete project lifecycle management
- **Client Management**: Comprehensive client database
- **Lead Management**: Sales lead tracking and management

## 🏗️ Architecture

- **Backend**: Flask with Firebase Admin SDK
- **Frontend**: HTML/CSS/JavaScript with Bootstrap
- **Database**: Firebase Firestore (with local JSON fallback)
- **Storage**: Firebase Storage
- **Authentication**: Firebase Auth + JWT
- **Real-time**: Firestore real-time listeners

## 📋 Prerequisites

- Python 3.8+
- Firebase project
- Service account credentials
- Modern web browser

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd trivanta-erp
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Firebase Setup

#### Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project: `trivanta-erp`
3. Enable the following services:
   - **Firestore Database** (Native mode)
   - **Storage**
   - **Authentication**

#### Step 2: Get Service Account Credentials

1. In Firebase Console, go to **Project Settings** → **Service Accounts**
2. Click **Generate New Private Key**
3. Download the JSON file
4. Rename it to `service-account-key.json`
5. Place it in the project root directory

**⚠️ Important**: Never commit this file to version control!

#### Step 3: Update Firebase Configuration

The Firebase configuration is already set up in the code, but verify these settings in `templates/base.html`:

```javascript
const firebaseConfig = {
  apiKey: "AIzaSyBwceYbtCryrZcTYvK38GtUNjEnvTVfqXQ",
  authDomain: "trivanta-erp.firebaseapp.com",
  projectId: "trivanta-erp",
  storageBucket: "trivanta-erp.firebasestorage.app",
  messagingSenderId: "1086746404611",
  appId: "1:1086746404611:web:f1b58ca02ab6496cc46b36",
  measurementId: "G-7NG8G150T9"
};
```

### 4. Initialize Firebase System

```bash
python initialize_firebase.py
```

This script will:
- Check service account credentials
- Initialize Firebase services
- Test Firebase operations
- Migrate existing data to Firebase

### 5. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:8080`

## 🔐 Default Login Credentials

- **Email**: `admin@trivantaedge.com`
- **Password**: `As@102005`
- **Role**: Admin

## 📁 Project Structure

```
trivanta-erp/
├── api/                    # API endpoints
├── routes/                 # Route handlers
│   ├── admin.py           # Admin portal routes
│   ├── manager.py         # Manager portal routes
│   └── employee.py        # Employee portal routes
├── templates/              # HTML templates
│   ├── admin/             # Admin portal templates
│   ├── manager/           # Manager portal templates
│   └── employee/          # Employee portal templates
├── static/                 # Static assets
│   └── js/                # JavaScript files
├── utils/                  # Utility modules
│   ├── firebase_config.py      # Firebase configuration
│   ├── firebase_data_manager.py # Data management
│   ├── firebase_auth.py        # Authentication
│   └── firebase_storage.py     # File storage
├── data/                   # Local data storage (fallback)
├── app.py                  # Main application
├── config.py               # Configuration
└── requirements.txt         # Python dependencies
```

## 🔥 Firebase Integration Details

### Data Collections

- **users**: User accounts and profiles
- **clients**: Client information and contacts
- **projects**: Project details and progress
- **employees**: Employee records
- **attendance**: Attendance tracking
- **leads**: Sales leads and prospects
- **tasks**: Task management

### Real-Time Features

- Live dashboard updates
- Real-time data synchronization
- Automatic UI updates
- Offline support with local fallback

### Security Rules

The system includes comprehensive Firebase security rules for:
- User authentication and authorization
- Role-based access control
- Data validation and sanitization
- File upload restrictions

## 🚨 Troubleshooting

### Common Issues

#### 1. Firebase Initialization Failed

**Symptoms**: Error messages about Firebase not being ready
**Solutions**:
- Verify service account credentials exist
- Check internet connection
- Ensure Firebase project is active
- Verify project ID matches configuration

#### 2. Permission Denied Errors

**Symptoms**: "Permission denied" or "Unauthorized" errors
**Solutions**:
- Check Firebase security rules
- Verify user authentication
- Ensure proper role assignments
- Check service account permissions

#### 3. Data Not Syncing

**Symptoms**: Changes not appearing in real-time
**Solutions**:
- Check browser console for errors
- Verify Firebase connection status
- Restart the application
- Check network connectivity

#### 4. File Upload Failures

**Symptoms**: Files not uploading to Firebase Storage
**Solutions**:
- Check Storage security rules
- Verify file size limits
- Check bucket permissions
- Ensure proper authentication

### Debug Mode

Enable debug logging by setting the environment variable:

```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
```

### Log Files

- **Application logs**: Check console output
- **Firebase logs**: Check `firebase_init.log`
- **Browser logs**: Check browser developer console

## 🔒 Security Considerations

- **Service Account**: Keep credentials secure and never commit to version control
- **Environment Variables**: Use environment variables for sensitive configuration
- **Firebase Rules**: Regularly review and update security rules
- **User Permissions**: Implement proper role-based access control
- **Data Validation**: Validate all input data on both client and server

## 📊 Performance Optimization

- **Indexing**: Create Firestore indexes for complex queries
- **Pagination**: Implement pagination for large datasets
- **Caching**: Use client-side caching for frequently accessed data
- **Batch Operations**: Use batch operations for multiple updates

## 🧪 Testing

Run the test suite to verify Firebase integration:

```bash
python test_firebase_integration.py
```

## 📈 Monitoring

- **Firebase Console**: Monitor usage, performance, and errors
- **Application Logs**: Check application logs for issues
- **Performance Metrics**: Monitor response times and throughput
- **Error Tracking**: Set up error monitoring and alerting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

1. Check the troubleshooting section above
2. Review Firebase documentation
3. Check application logs
4. Create an issue in the repository

## 🔄 Updates and Maintenance

- **Regular Updates**: Keep Firebase SDK versions updated
- **Security Patches**: Apply security updates promptly
- **Backup**: Regular data backups and testing
- **Monitoring**: Continuous monitoring of system health

## 🎯 Roadmap

- [ ] Enhanced analytics and reporting
- [ ] Mobile application
- [ ] Advanced workflow automation
- [ ] Integration with external services
- [ ] Multi-language support
- [ ] Advanced user management
- [ ] API rate limiting
- [ ] Advanced caching strategies

---

**Note**: This ERP system is designed for production use with proper security measures. Always follow security best practices and regularly update dependencies.
