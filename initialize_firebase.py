#!/usr/bin/env python3
"""
Firebase Initialization Script for Trivanta Edge ERP
Initializes Firebase services and migrates data from local storage
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('firebase_init.log')
    ]
)
logger = logging.getLogger(__name__)

def check_service_account():
    """Check if service account credentials are available"""
    service_account_paths = [
        'service-account-key.json',
        'firebase-service-account.json',
        'trivanta-erp-firebase-adminsdk.json',
        os.path.expanduser('~/.config/firebase/service-account.json')
    ]
    
    # Check environment variable
    if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        if os.path.exists(os.getenv('GOOGLE_APPLICATION_CREDENTIALS')):
            logger.info(f"✅ Service account found at: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
            return True
        else:
            logger.warning(f"⚠️ Service account path in environment variable does not exist: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
    
    # Check common locations
    for path in service_account_paths:
        if os.path.exists(path):
            logger.info(f"✅ Service account found at: {path}")
            return True
    
    logger.warning("⚠️ No service account credentials found")
    return False

def create_service_account_template():
    """Create a template for service account credentials"""
    template = {
        "type": "service_account",
        "project_id": "trivanta-erp",
        "private_key_id": "YOUR_PRIVATE_KEY_ID",
        "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n",
        "client_email": "firebase-adminsdk-xxxxx@trivanta-erp.iam.gserviceaccount.com",
        "client_id": "YOUR_CLIENT_ID",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40trivanta-erp.iam.gserviceaccount.com"
    }
    
    import json
    with open('service-account-template.json', 'w') as f:
        json.dump(template, f, indent=2)
    
    logger.info("📝 Service account template created: service-account-template.json")
    logger.info("📋 Please fill in your actual credentials and rename to service-account-key.json")

def initialize_firebase_system():
    """Initialize the complete Firebase system"""
    logger.info("🚀 Initializing Firebase System for Trivanta Edge ERP...")
    
    try:
        # Check service account credentials
        if not check_service_account():
            logger.warning("⚠️ No service account credentials found")
            logger.info("📋 Creating service account template...")
            create_service_account_template()
            logger.info("📖 Please follow the setup instructions below:")
            logger.info("   1. Download service account key from Firebase Console")
            logger.info("   2. Rename it to 'service-account-key.json'")
            logger.info("   3. Place it in the project root directory")
            logger.info("   4. Run this script again")
            return False
        
        # Step 1: Initialize Firebase Configuration
        logger.info("📋 Step 1: Initializing Firebase Configuration...")
        from utils.firebase_config import get_firebase_config
        firebase_config = get_firebase_config()
        
        if firebase_config.initialize():
            logger.info("✅ Firebase configuration initialized successfully")
        else:
            logger.error("❌ Firebase configuration initialization failed")
            return False
        
        # Step 2: Initialize Firebase Data Manager
        logger.info("📊 Step 2: Initializing Firebase Data Manager...")
        from utils.firebase_data_manager import FirebaseDataManager
        data_manager = FirebaseDataManager()
        
        if data_manager.firebase_ready:
            logger.info("✅ Firebase data manager initialized successfully")
        else:
            logger.warning("⚠️ Firebase data manager not ready, using local storage")
        
        # Step 3: Initialize Firebase Auth Service
        logger.info("🔐 Step 3: Initializing Firebase Auth Service...")
        try:
            from utils.firebase_auth import get_firebase_auth_service
            auth_service = get_firebase_auth_service()
            
            if auth_service.initialize():
                logger.info("✅ Firebase auth service initialized successfully")
            else:
                logger.warning("⚠️ Firebase auth service initialization failed (may need service account)")
        except Exception as e:
            logger.warning(f"⚠️ Firebase auth service initialization failed: {e}")
        
        # Step 4: Initialize Firebase Storage Service
        logger.info("📁 Step 4: Initializing Firebase Storage Service...")
        try:
            from utils.firebase_storage import get_firebase_storage_service
            storage_service = get_firebase_storage_service()
            
            if storage_service.initialize():
                logger.info("✅ Firebase storage service initialized successfully")
            else:
                logger.warning("⚠️ Firebase storage service initialization failed (may need service account)")
        except Exception as e:
            logger.warning(f"⚠️ Firebase storage service initialization failed: {e}")
        
        # Step 5: Test Firebase Operations
        logger.info("🧪 Step 5: Testing Firebase Operations...")
        try:
            # Test creating a test document
            if data_manager.firebase_ready:
                test_data = {
                    "name": "Test Document",
                    "type": "test",
                    "created_at": "2024-01-01T00:00:00Z"
                }
                
                # Try to create in test collection
                try:
                    doc_ref = firebase_config.db.collection('test').add(test_data)
                    logger.info(f"✅ Test document created successfully: {doc_ref[1].id}")
                    
                    # Clean up test document
                    firebase_config.db.collection('test').document(doc_ref[1].id).delete()
                    logger.info("✅ Test document cleaned up")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Test document creation failed: {e}")
            
        except Exception as e:
            logger.warning(f"⚠️ Firebase operations test failed: {e}")
        
        # Step 6: Data Migration
        if data_manager.firebase_ready:
            logger.info("🔄 Step 6: Migrating Data to Firebase...")
            try:
                if data_manager.migrate_to_firebase():
                    logger.info("✅ Data migration completed successfully")
                else:
                    logger.warning("⚠️ Data migration failed")
            except Exception as e:
                logger.warning(f"⚠️ Data migration failed: {e}")
        
        logger.info("🎉 Firebase System Initialization Completed Successfully!")
        logger.info("📊 System Status:")
        logger.info(f"   Project ID: {firebase_config.config['projectId']}")
        logger.info(f"   Storage Bucket: {firebase_config.config['storageBucket']}")
        logger.info(f"   Firebase Ready: {firebase_config.is_ready()}")
        logger.info(f"   Data Manager Ready: {data_manager.firebase_ready}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Firebase system initialization failed: {e}")
        logger.error("Please check the error logs and ensure Firebase is properly configured")
        return False

def main():
    """Main function"""
    logger.info("🔥 Trivanta Edge ERP - Firebase Initialization")
    logger.info("This script will initialize the Firebase system and prepare it for use.")
    logger.info("")
    logger.info("Prerequisites:")
    logger.info("  - Firebase project configured")
    logger.info("  - Service account key downloaded")
    logger.info("  - Required Python packages installed")
    logger.info("")
    
    # Check if user wants to continue
    try:
        response = input("Do you want to continue with Firebase initialization? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            logger.info("Initialization cancelled by user")
            return
    except KeyboardInterrupt:
        logger.info("\nInitialization cancelled by user")
        return
    
    logger.info("")
    
    # Initialize Firebase system
    success = initialize_firebase_system()
    
    if success:
        logger.info("\n🎯 Firebase system is ready to use!")
        logger.info("You can now run your ERP application with Firebase integration.")
    else:
        logger.error("\n💥 Firebase system initialization failed!")
        logger.error("Please check the logs and fix any issues before running the application.")

if __name__ == "__main__":
    main()
