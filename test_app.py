#!/usr/bin/env python3
"""
Test script for Trivanta ERP application
"""

import requests
import time
import sys

def test_application():
    """Test if the application is running and accessible"""
    
    # Wait a moment for the server to start
    time.sleep(2)
    
    try:
        # Test health check endpoint
        print("Testing health check endpoint...")
        response = requests.get('http://127.0.0.1:8080/api/health', timeout=5)
        if response.status_code == 200:
            print("✓ Health check passed")
            print(f"  Response: {response.json()}")
        else:
            print(f"✗ Health check failed with status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Health check failed with error: {e}")
        return False
    
    try:
        # Test login page
        print("\nTesting login page...")
        response = requests.get('http://127.0.0.1:8080/login', timeout=5)
        if response.status_code == 200 and 'login' in response.text.lower():
            print("✓ Login page loads successfully")
        else:
            print(f"✗ Login page failed with status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Login page failed with error: {e}")
        return False
    
    try:
        # Test admin login
        print("\nTesting admin login...")
        session = requests.Session()
        
        # Get login page first to get any CSRF tokens
        response = session.get('http://127.0.0.1:8080/login', timeout=5)
        
        # Attempt admin login
        login_data = {
            'email': 'admin@trivantaedge.com',
            'password': 'admin123'
        }
        
        response = session.post('http://127.0.0.1:8080/login', data=login_data, timeout=5, allow_redirects=False)
        
        if response.status_code in [302, 303]:  # Redirect indicates successful login
            print("✓ Admin login successful")
            
            # Test admin dashboard
            print("\nTesting admin dashboard...")
            response = session.get('http://127.0.0.1:8080/admin/dashboard', timeout=5)
            if response.status_code == 200:
                print("✓ Admin dashboard loads successfully")
                return True
            else:
                print(f"✗ Admin dashboard failed with status: {response.status_code}")
                return False
        else:
            print(f"✗ Admin login failed with status: {response.status_code}")
            print(f"  Response content: {response.text[:200]}...")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Admin login test failed with error: {e}")
        return False

if __name__ == '__main__':
    print("Starting Trivanta ERP Application Tests...")
    print("=" * 50)
    
    success = test_application()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! The application is working correctly.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Check the output above for details.")
        sys.exit(1)
