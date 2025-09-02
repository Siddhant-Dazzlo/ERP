#!/usr/bin/env python3
"""
Railway Data Initialization Script
Ensures all users and data are properly set up on Railway
"""

import os
import json
from datetime import datetime

def create_railway_data():
    """Create initial data for Railway deployment"""
    
    # Check if we're on Railway
    is_railway = os.environ.get('RAILWAY_ENVIRONMENT')
    print(f"🚀 Initializing data for {'Railway' if is_railway else 'Local'} environment")
    
    # Data structure
    data = {
        "users": [
            {
                "id": "admin_001",
                "name": "Siddhant_MD",
                "email": "admin@trivantaedge.com",
                "password": "$2b$12$KAn7rjfILk35KVvjzOkUYuQoEuNf2Po7phPa6FZsRwe6XvfF3XfOS",
                "role": "admin",
                "department": "Administration",
                "created_at": datetime.now().isoformat(),
                "status": "active",
                "api_key": "grWwCx8rQMryw-pfjcWdLhtyNvtGbRh3lu3zmNP_dLE"
            },
            {
                "name": "New",
                "email": "sidsur23@gmail.com",
                "password": "$2b$12$Tjiflz6jrIPiUcx49bxoFu571SBiQx1EOznjFneOKIl2nhCqrPlrq",
                "role": "manager",
                "department": "Operations",
                "id": "user_002",
                "created_at": datetime.now().isoformat(),
                "status": "active",
                "api_key": "D18IAHMsxC0-VEMh0c_z04todlwG3iQ2o9a86lqta-A"
            },
            {
                "name": "Siddhant suryavanshi",
                "email": "sidsur70@gmail.com",
                "password": "$2b$12$p4.A0UTGHjsRBK12h5LEJ.wxg.AknwYFaOB8PkJfP3LTUZi4.ulRa",
                "role": "employee",
                "department": "development",
                "id": "user_003",
                "created_at": datetime.now().isoformat(),
                "status": "active",
                "api_key": "AsJOvvYgifBHlwgFRcmbFB8us6Xqp0BrqjDt4pHqmsA"
            }
        ],
        "clients": [],
        "projects": [],
        "employees": [],
        "attendance": [],
        "leads": [],
        "tasks": [],
        "daily_otp": "",
        "analytics": {
            "installation_revenue": 0,
            "manufacturing_revenue": 0,
            "total_projects": 0,
            "active_employees": 0
        }
    }
    
    # Determine file path
    if is_railway:
        data_dir = '/app/data'
        data_file = '/app/data/trivanta_erp.json'
    else:
        data_dir = 'data'
        data_file = 'data/trivanta_erp.json'
    
    # Create directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    print(f"📁 Created directory: {data_dir}")
    
    # Write data file
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"💾 Data written to: {data_file}")
    print(f"👥 Users created: {len(data['users'])}")
    
    # Print user details
    for user in data['users']:
        print(f"   - {user['name']} ({user['role']}) - {user['email']}")
    
    print("✅ Railway data initialization completed!")
    return True

if __name__ == "__main__":
    create_railway_data()
