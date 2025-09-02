#!/usr/bin/env python3
"""
Test User Credentials
Verifies that all users can authenticate properly
"""

from utils.firebase_data_manager import FirebaseDataManager
from utils.security import security_manager

def test_user_credentials():
    """Test all user credentials"""
    print("🧪 Testing User Credentials...")
    print("=" * 50)
    
    # Initialize data manager
    data_manager = FirebaseDataManager()
    
    # Test users
    test_users = [
        {
            "name": "Admin User",
            "email": "admin@trivantaedge.com",
            "password": "As@102005",
            "expected_role": "admin"
        },
        {
            "name": "Manager User", 
            "email": "sidsur23@gmail.com",
            "password": "password123",  # You'll need to set this
            "expected_role": "manager"
        },
        {
            "name": "Employee User",
            "email": "sidsur70@gmail.com", 
            "password": "password123",  # You'll need to set this
            "expected_role": "employee"
        }
    ]
    
    results = []
    
    for user_test in test_users:
        print(f"\n🔍 Testing {user_test['name']}...")
        
        try:
            # Try to authenticate
            user = data_manager.authenticate_user(user_test['email'], user_test['password'])
            
            if user:
                print(f"✅ {user_test['name']} - Authentication SUCCESS")
                print(f"   Role: {user.get('role')} (Expected: {user_test['expected_role']})")
                print(f"   Status: {user.get('status')}")
                
                if user.get('role') == user_test['expected_role']:
                    results.append(True)
                else:
                    results.append(False)
                    print(f"   ⚠️ Role mismatch!")
            else:
                print(f"❌ {user_test['name']} - Authentication FAILED")
                results.append(False)
                
        except Exception as e:
            print(f"💥 {user_test['name']} - Error: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 CREDENTIALS TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"🎯 Overall Result: {passed}/{total} users authenticated successfully")
    
    if passed == total:
        print("🎉 All users working! Ready for Railway deployment!")
    else:
        print("⚠️ Some users need attention before deployment")
        
        # Show which users failed
        for i, (user_test, result) in enumerate(zip(test_users, results)):
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {user_test['name']}: {status}")
    
    return passed == total

if __name__ == "__main__":
    test_user_credentials()
