#!/usr/bin/env python3
"""
Reset User Passwords
Sets working passwords for all users
"""

from utils.firebase_data_manager import FirebaseDataManager
from utils.security import security_manager

def reset_user_passwords():
    """Reset passwords for all users"""
    print("🔐 Resetting User Passwords...")
    print("=" * 50)
    
    # Initialize data manager
    data_manager = FirebaseDataManager()
    
    # New passwords (you can change these)
    new_passwords = {
        "admin@trivantaedge.com": "As@102005",      # Admin - keep existing
        "sidsur23@gmail.com": "Manager@2024",       # Manager - new password
        "sidsur70@gmail.com": "Employee@2024"       # Employee - new password
    }
    
    updated_users = []
    
    for email, new_password in new_passwords.items():
        print(f"\n🔍 Updating {email}...")
        
        try:
            # Find user by email
            user = data_manager.get_user_by_email(email)
            
            if user:
                # Hash new password
                hashed_password = security_manager.hash_password(new_password)
                
                # Update user password
                user['password'] = hashed_password
                
                # Update in data manager
                if data_manager.update_user(user['id'], user):
                    print(f"✅ {email} - Password updated successfully")
                    print(f"   New password: {new_password}")
                    updated_users.append(email)
                else:
                    print(f"❌ {email} - Failed to update password")
            else:
                print(f"❌ {email} - User not found")
                
        except Exception as e:
            print(f"💥 {email} - Error: {e}")
    
    # Save updated data
    if updated_users:
        data_manager.save_data()
        print(f"\n💾 Data saved with {len(updated_users)} updated users")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 PASSWORD RESET SUMMARY")
    print("=" * 50)
    
    for email in updated_users:
        password = new_passwords[email]
        print(f"✅ {email} - {password}")
    
    print(f"\n🎯 Total users updated: {len(updated_users)}")
    
    if len(updated_users) == len(new_passwords):
        print("🎉 All passwords reset! Ready for Railway deployment!")
    else:
        print("⚠️ Some passwords need manual attention")
    
    return len(updated_users) == len(new_passwords)

if __name__ == "__main__":
    reset_user_passwords()
