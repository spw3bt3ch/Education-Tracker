#!/usr/bin/env python3
"""
Test script to verify super admin access
"""

import os
import sys
import requests

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User

def test_super_admin():
    """Test super admin access"""
    with app.app_context():
        try:
            # Check if super admin exists
            super_admin = User.query.filter_by(username='superadmin').first()
            if not super_admin:
                print("❌ Super admin account not found!")
                return False
            
            print("✅ Super admin account found:")
            print(f"  Username: {super_admin.username}")
            print(f"  Email: {super_admin.email}")
            print(f"  Role: {super_admin.role}")
            print(f"  School ID: {super_admin.school_id}")
            
            # Test the super admin route
            with app.test_client() as client:
                # First login
                login_response = client.post('/login', data={
                    'username': 'superadmin',
                    'password': 'superadmin123'
                }, follow_redirects=True)
                
                print(f"\nLogin response status: {login_response.status_code}")
                
                # Then try to access super admin dashboard
                dashboard_response = client.get('/super-admin')
                print(f"Dashboard response status: {dashboard_response.status_code}")
                
                if dashboard_response.status_code == 200:
                    print("✅ Super admin dashboard accessible!")
                    return True
                else:
                    print("❌ Super admin dashboard not accessible!")
                    print(f"Response: {dashboard_response.data.decode()}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error testing super admin: {e}")
            return False

if __name__ == '__main__':
    print("Testing Super Admin Access...")
    print("=" * 40)
    
    success = test_super_admin()
    
    if success:
        print("\n" + "=" * 40)
        print("🎉 Super admin access is working!")
        print("\nTo access the super admin dashboard:")
        print("1. Go to: http://127.0.0.1:5000/login")
        print("2. Login with:")
        print("   Username: superadmin")
        print("   Password: superadmin123")
        print("3. Then go to: http://127.0.0.1:5000/super-admin")
    else:
        print("\n" + "=" * 40)
        print("❌ Super admin access is not working")
        sys.exit(1)
