#!/usr/bin/env python3
"""
Quick Route Test Script for Trivanta ERP
========================================

This script tests if the employee routes are working correctly.
"""

import requests
import json

def test_employee_routes():
    """Test employee routes for functionality"""
    
    base_url = "http://127.0.0.1:8080"
    
    print("🔧 Testing Employee Routes")
    print("=" * 40)
    
    # Test routes that should work
    routes_to_test = [
        "/employee/dashboard",
        "/employee/clients", 
        "/employee/tasks",
        "/employee/projects",
        "/employee/attendance",
        "/employee/leads",
        "/employee/profile",
        "/employee/reports"
    ]
    
    for route in routes_to_test:
        try:
            response = requests.get(f"{base_url}{route}", allow_redirects=False)
            status = response.status_code
            if status == 200:
                print(f"✅ {route} - OK (200)")
            elif status == 302:
                print(f"🔄 {route} - Redirect (302) - Likely needs login")
            elif status == 404:
                print(f"❌ {route} - Not Found (404)")
            else:
                print(f"⚠️  {route} - Status {status}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {route} - Connection Error (Flask app not running)")
        except Exception as e:
            print(f"❌ {route} - Error: {e}")
    
    print("\n📋 Test Results Summary:")
    print("-" * 30)
    print("✅ 200: Route working correctly")
    print("🔄 302: Route redirecting (needs authentication)")
    print("❌ 404: Route not found")
    print("❌ Connection Error: Flask app not running")

if __name__ == "__main__":
    test_employee_routes()
