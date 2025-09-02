#!/usr/bin/env python3
"""
Simple Firebase Integration Test for Trivanta Edge ERP
Quick test to verify Firebase is working
"""

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_firebase_basic():
    """Test basic Firebase functionality"""
    logger.info("🧪 Testing Basic Firebase Functionality...")
    
    try:
        # Test Firebase configuration
        from utils.firebase_config import get_firebase_config
        firebase_config = get_firebase_config()
        
        logger.info(f"✅ Firebase config loaded: {firebase_config.config['projectId']}")
        
        # Test initialization
        if firebase_config.initialize():
            logger.info("✅ Firebase configuration initialized")
            
            # Test if ready
            if firebase_config.is_ready():
                logger.info("✅ Firebase is ready")
                
                # Test basic Firestore operation
                try:
                    db = firebase_config.get_firestore_client()
                    test_collection = db.collection('test')
                    logger.info("✅ Firestore client working")
                    
                    # Test write operation
                    test_data = {"test": "data", "timestamp": "2024-01-01"}
                    doc_ref = test_collection.add(test_data)
                    logger.info(f"✅ Write test passed: {doc_ref[1].id}")
                    
                    # Test read operation
                    doc = test_collection.document(doc_ref[1].id).get()
                    if doc.exists:
                        logger.info("✅ Read test passed")
                    else:
                        logger.error("❌ Read test failed")
                    
                    # Clean up test data
                    test_collection.document(doc_ref[1].id).delete()
                    logger.info("✅ Cleanup test passed")
                    
                    return True
                    
                except Exception as e:
                    logger.error(f"❌ Firestore operations failed: {e}")
                    return False
            else:
                logger.warning("⚠️ Firebase not ready")
                return False
        else:
            logger.error("❌ Firebase initialization failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Firebase test error: {e}")
        return False

def test_data_manager():
    """Test data manager with Firebase"""
    logger.info("🧪 Testing Data Manager with Firebase...")
    
    try:
        from utils.firebase_data_manager import FirebaseDataManager
        data_manager = FirebaseDataManager()
        
        logger.info(f"✅ Data manager initialized")
        logger.info(f"   Firebase ready: {getattr(data_manager, 'firebase_ready', False)}")
        logger.info(f"   Using local storage: {getattr(data_manager, 'use_local_storage', True)}")
        
        # Test basic operations
        test_user = {
            "name": "Test User",
            "email": "test@example.com",
            "role": "employee",
            "department": "Testing"
        }
        
        # Create user
        created_user = data_manager.create_user(test_user)
        if created_user and created_user.get('id'):
            logger.info(f"✅ User creation test passed: {created_user['id']}")
        else:
            logger.error("❌ User creation test failed")
            return False
        
        # Get user
        retrieved_user = data_manager.get_user_by_email("test@example.com")
        if retrieved_user and retrieved_user.get('name') == "Test User":
            logger.info("✅ User retrieval test passed")
        else:
            logger.error("❌ User retrieval test failed")
            return False
        
        # Clean up
        if data_manager.delete_user(created_user['id']):
            logger.info("✅ User deletion test passed")
        else:
            logger.error("❌ User deletion test failed")
            return False
        
        logger.info("✅ Data manager test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Data manager test error: {e}")
        return False

def main():
    """Main test function"""
    logger.info("🔥 Trivanta Edge ERP - Simple Firebase Test")
    logger.info("=" * 50)
    
    # Run tests
    tests = [
        ("Basic Firebase", test_firebase_basic),
        ("Data Manager", test_data_manager)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n🔍 Running {test_name} Test...")
        try:
            if test_func():
                logger.info(f"✅ {test_name} Test: PASSED")
                passed += 1
            else:
                logger.error(f"❌ {test_name} Test: FAILED")
        except Exception as e:
            logger.error(f"💥 {test_name} Test: ERROR - {e}")
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 TEST RESULTS SUMMARY")
    logger.info("=" * 50)
    logger.info(f"🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Firebase integration is working correctly.")
    elif passed > 0:
        logger.info("⚠️ Some tests passed. Firebase integration has partial functionality.")
    else:
        logger.error("💥 All tests failed. Firebase integration needs attention.")
    
    return passed == total

if __name__ == "__main__":
    main()
