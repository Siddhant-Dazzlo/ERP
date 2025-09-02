#!/usr/bin/env python3
"""
Employee Login and Route Test Script
===================================

This script tests employee login and then tests protected routes.
"""

import requests
import json

def test_employee_login_and_routes():
    """Test employee login and then test protected routes"""
    
    base_url = "http://127.0.0.1:8080"
    session = requests.Session()
    
    print("🔧 Testing Employee Login and Routes")
    print("=" * 50)
    
    # Step 1: Test login page
    print("\n📋 Step 1: Testing Login Page")
    print("-" * 30)
    try:
        response = session.get(f"{base_url}/login")
        if response.status_code == 200:
            print("✅ Login page accessible")
        else:
            print(f"❌ Login page error: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Login page error: {e}")
        return
    
    # Step 2: Attempt login
    print("\n📋 Step 2: Attempting Employee Login")
    print("-" * 30)
    
    login_data = {
        'email': 'employee@trivantaedge.com',
        'password': 'Employee@123'
    }
    
    try:
        response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        print(f"Login response status: {response.status_code}")
        
        if response.status_code == 302:
            print("✅ Login successful - redirecting")
            # Follow the redirect
            redirect_url = response.headers.get('Location')
            print(f"Redirecting to: {redirect_url}")
            
            if redirect_url:
                response = session.get(f"{base_url}{redirect_url}", allow_redirects=False)
                print(f"Dashboard response: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ Successfully accessed employee dashboard")
                    
                    # Step 3: Test protected routes
                    print("\n📋 Step 3: Testing Protected Routes")
                    print("-" * 30)
                    
                    protected_routes = [
                        "/employee/clients",
                        "/employee/tasks", 
                        "/employee/projects",
                        "/employee/attendance",
                        "/employee/leads",
                        "/employee/profile",
                        "/employee/reports"
                    ]
                    
                    for route in protected_routes:
                        try:
                            response = session.get(f"{base_url}{route}", allow_redirects=False)
                            if response.status_code == 200:
                                print(f"✅ {route} - Working")
                            elif response.status_code == 302:
                                print(f"🔄 {route} - Redirecting (might be another redirect)")
                            else:
                                print(f"❌ {route} - Status {response.status_code}")
                        except Exception as e:
                            print(f"❌ {route} - Error: {e}")
                    
                else:
                    print(f"❌ Dashboard access failed: {response.status_code}")
                    print("Response content:", response.text[:200])
            else:
                print("❌ No redirect URL found")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print("Response content:", response.text[:200])
            
    except Exception as e:
        print(f"❌ Login request error: {e}")
    
    print("\n📋 Test Complete")
    print("=" * 50)

if __name__ == "__main__":
    test_employee_login_and_routes()
