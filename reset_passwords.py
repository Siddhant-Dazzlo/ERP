#!/usr/bin/env python3
"""
Password Reset Script for Trivanta ERP
=====================================

This script resets the test user passwords to known values for testing purposes.
"""

import json
import os
from utils.security import security_manager

def reset_test_passwords():
    """Reset test user passwords to known values"""
    
    # Known test passwords
    test_passwords = {
        "manager@trivantaedge.com": "Manager@123",
        "employee@trivantaedge.com": "Employee@123"
    }
    
    # Load current data
    data_file = 'data/trivanta_erp.json'
    if not os.path.exists(data_file):
        print("❌ Data file not found!")
        return
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    # Update passwords
    updated = False
    for user in data.get('users', []):
        if user['email'] in test_passwords:
            old_password = user['password']
            new_password = security_manager.hash_password(test_passwords[user['email']])
            user['password'] = new_password
            updated = True
            print(f"✅ Updated password for {user['email']}")
            print(f"   Old hash: {old_password[:20]}...")
            print(f"   New hash: {new_password[:20]}...")
    
    if updated:
        # Save updated data
        with open(data_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print("\n🎉 Passwords updated successfully!")
        print("\n📋 Test Credentials:")
        print("=" * 40)
        print("👑 Admin: admin@trivantaedge.com / admin123")
        print("👔 Manager: manager@trivantaedge.com / Manager@123")
        print("👷 Employee: employee@trivantaedge.com / Employee@123")
        print("\n⚠️  Note: These are test credentials only!")
    else:
        print("❌ No users found to update!")

if __name__ == "__main__":
    print("🔧 Trivanta ERP - Password Reset Tool")
    print("=" * 40)
    reset_test_passwords()
