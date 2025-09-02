#!/usr/bin/env python3
"""
Firebase Integration Test Script for Trivanta Edge ERP
Tests all Firebase services and functionality
"""

import os
import sys
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('firebase_test.log')
    ]
)
logger = logging.getLogger(__name__)

def test_firebase_config():
    """Test Firebase configuration"""
    logger.info("🧪 Testing Firebase Configuration...")
    
    try:
        from utils.firebase_config import get_firebase_config
        firebase_config = get_firebase_config()
        
        # Test configuration loading
        config = firebase_config.get_config()
        logger.info(f"✅ Firebase config loaded: {config['projectId']}")
        
        # Test initialization
        if firebase_config.initialize():
            logger.info("✅ Firebase configuration test passed")
            return True
        else:
            logger.error("❌ Firebase configuration test failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Firebase configuration test error: {e}")
        return False

def test_firebase_data_manager():
    """Test Firebase data manager"""
    logger.info("🧪 Testing Firebase Data Manager...")
    
    try:
        from utils.firebase_data_manager import FirebaseDataManager
        data_manager = FirebaseDataManager()
        
        # Test basic operations
        test_user = {
            "name": "Test User",
            "email": "test@example.com",
            "role": "employee",
            "department": "Testing"
        }
        
        # Test user creation
        created_user = data_manager.create_user(test_user)
        if created_user and created_user.get('id'):
            logger.info(f"✅ User creation test passed: {created_user['id']}")
        else:
            logger.error("❌ User creation test failed")
            return False
        
        # Test user retrieval
        retrieved_user = data_manager.get_user_by_email("test@example.com")
        if retrieved_user and retrieved_user.get('name') == "Test User":
            logger.info("✅ User retrieval test passed")
        else:
            logger.error("❌ User retrieval test failed")
            return False
        
        # Test user update
        update_data = {"status": "inactive"}
        if data_manager.update_user(created_user['id'], update_data):
            logger.info("✅ User update test passed")
        else:
            logger.error("❌ User update test failed")
            return False
        
        # Test user deletion
        if data_manager.delete_user(created_user['id']):
            logger.info("✅ User deletion test passed")
        else:
            logger.error("❌ User deletion test failed")
            return False
        
        logger.info("✅ Firebase data manager test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Firebase data manager test error: {e}")
        return False

def test_firebase_auth():
    """Test Firebase authentication service"""
    logger.info("🧪 Testing Firebase Auth Service...")
    
    try:
        from utils.firebase_auth import get_firebase_auth_service
        auth_service = get_firebase_auth_service()
        
        if auth_service.initialize():
            logger.info("✅ Firebase auth service test passed")
            return True
        else:
            logger.warning("⚠️ Firebase auth service test failed (may need service account)")
            return False
            
    except Exception as e:
        logger.error(f"❌ Firebase auth service test error: {e}")
        return False

def test_firebase_storage():
    """Test Firebase storage service"""
    logger.info("🧪 Testing Firebase Storage Service...")
    
    try:
        from utils.firebase_storage import get_firebase_storage_service
        storage_service = get_firebase_storage_service()
        
        if storage_service.initialize():
            logger.info("✅ Firebase storage service test passed")
            return True
        else:
            logger.warning("⚠️ Firebase storage service test failed (may need service account)")
            return False
            
    except Exception as e:
        logger.error(f"❌ Firebase storage service test error: {e}")
        return False

def test_data_operations():
    """Test various data operations"""
    logger.info("🧪 Testing Data Operations...")
    
    try:
        from utils.firebase_data_manager import FirebaseDataManager
        data_manager = FirebaseDataManager()
        
        # Test client operations
        test_client = {
            "name": "Test Client",
            "email": "client@example.com",
            "phone": "+1234567890",
            "company": "Test Company",
            "business_type": "installation"
        }
        
        created_client = data_manager.create_client(test_client)
        if created_client and created_client.get('id'):
            logger.info(f"✅ Client creation test passed: {created_client['id']}")
        else:
            logger.error("❌ Client creation test failed")
            return False
        
        # Test project operations
        test_project = {
            "name": "Test Project",
            "type": "installation",
            "client_id": created_client['id'],
            "description": "Test project description",
            "budget": 50000
        }
        
        created_project = data_manager.create_project(test_project)
        if created_project and created_project.get('id'):
            logger.info(f"✅ Project creation test passed: {created_project['id']}")
        else:
            logger.error("❌ Project creation test failed")
            return False
        
        # Test lead operations
        test_lead = {
            "name": "Test Lead",
            "email": "lead@example.com",
            "company": "Test Company",
            "business_type": "both",
            "source": "website"
        }
        
        created_lead = data_manager.create_lead(test_lead)
        if created_lead and created_lead.get('id'):
            logger.info(f"✅ Lead creation test passed: {created_lead['id']}")
        else:
            logger.error("❌ Lead creation test failed")
            return False
        
        # Clean up test data
        data_manager.delete_project(created_project['id'])
        data_manager.delete_client(created_client['id'])
        data_manager.delete_lead(created_lead['id'])
        logger.info("✅ Test data cleanup completed")
        
        logger.info("✅ Data operations test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Data operations test error: {e}")
        return False

def test_firebase_connectivity():
    """Test Firebase connectivity and basic operations"""
    logger.info("🧪 Testing Firebase Connectivity...")
    
    try:
        from utils.firebase_config import get_firebase_config
        firebase_config = get_firebase_config()
        
        if not firebase_config.is_ready():
            logger.warning("⚠️ Firebase not ready, skipping connectivity test")
            return False
        
        # Test basic Firestore operations
        db = firebase_config.get_firestore_client()
        
        # Test collection creation
        test_data = {
            "test_field": "test_value",
            "timestamp": datetime.now().isoformat()
        }
        
        doc_ref = db.collection('test').add(test_data)
        if doc_ref and doc_ref[1].id:
            logger.info(f"✅ Firestore write test passed: {doc_ref[1].id}")
        else:
            logger.error("❌ Firestore write test failed")
            return False
        
        # Test document reading
        doc = db.collection('test').document(doc_ref[1].id).get()
        if doc.exists and doc.to_dict()['test_field'] == 'test_value':
            logger.info("✅ Firestore read test passed")
        else:
            logger.error("❌ Firestore read test failed")
            return False
        
        # Test document deletion
        db.collection('test').document(doc_ref[1].id).delete()
        logger.info("✅ Firestore delete test passed")
        
        logger.info("✅ Firebase connectivity test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Firebase connectivity test error: {e}")
        return False

def run_all_tests():
    """Run all Firebase integration tests"""
    logger.info("🚀 Starting Firebase Integration Tests...")
    logger.info("=" * 60)
    
    tests = [
        ("Firebase Configuration", test_firebase_config),
        ("Firebase Data Manager", test_firebase_data_manager),
        ("Firebase Auth Service", test_firebase_auth),
        ("Firebase Storage Service", test_firebase_storage),
        ("Data Operations", test_data_operations),
        ("Firebase Connectivity", test_firebase_connectivity)
    ]
    
    results = []
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n🔍 Running {test_name} Test...")
        try:
            if test_func():
                logger.info(f"✅ {test_name} Test: PASSED")
                results.append((test_name, True))
                passed += 1
            else:
                logger.error(f"❌ {test_name} Test: FAILED")
                results.append((test_name, False))
        except Exception as e:
            logger.error(f"💥 {test_name} Test: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST RESULTS SUMMARY")
    logger.info("=" * 60)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Firebase integration is working correctly.")
    elif passed > total // 2:
        logger.info("⚠️ Some tests failed. Firebase integration has issues that need attention.")
    else:
        logger.error("💥 Most tests failed. Firebase integration needs significant fixes.")
    
    return passed == total

def main():
    """Main function"""
    logger.info("🔥 Trivanta Edge ERP - Firebase Integration Testing")
    logger.info("This script will test all Firebase services and functionality.")
    logger.info("")
    
    # Check if user wants to continue
    try:
        response = input("Do you want to run Firebase integration tests? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            logger.info("Testing cancelled by user")
            return
    except KeyboardInterrupt:
        logger.info("\nTesting cancelled by user")
        return
    
    logger.info("")
    
    # Run all tests
    success = run_all_tests()
    
    if success:
        logger.info("\n🎯 Firebase integration testing completed successfully!")
        logger.info("Your Firebase setup is working correctly.")
    else:
        logger.error("\n💥 Firebase integration testing failed!")
        logger.error("Please check the logs and fix any issues.")

if __name__ == "__main__":
    main()
