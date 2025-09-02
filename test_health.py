#!/usr/bin/env python3
"""Test health endpoint for Railway deployment"""

from app import app

def test_health():
    """Test the health endpoint"""
    with app.test_client() as client:
        print("🧪 Testing health endpoint...")
        
        # Test health endpoint
        response = client.get('/health')
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.get_json()
            print("✅ Health check successful!")
            print(f"Response: {data}")
        else:
            print("❌ Health check failed!")
            print(f"Response: {response.data}")
        
        return response.status_code == 200

if __name__ == "__main__":
    test_health()
