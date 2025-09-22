#!/usr/bin/env python3
"""
Script to create a super admin account for EduTrack
"""

import os
import sys
from werkzeug.security import generate_password_hash

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User

def create_super_admin():
    """Create super admin account"""
    with app.app_context():
        try:
            # Check if super admin already exists
            existing_admin = User.query.filter_by(username='superadmin').first()
            if existing_admin:
                print("✅ Super admin account already exists!")
                print(f"Username: superadmin")
                print(f"Email: {existing_admin.email}")
                print(f"Role: {existing_admin.role}")
                return True
            
            # Create super admin
            super_admin_password = 'superadmin123'
            super_admin = User(
                username='superadmin',
                email='superadmin@edutrack.com',
                password_hash=generate_password_hash(super_admin_password),
                role='super_admin',
                first_name='Super',
                last_name='Admin',
                school_id=None  # Super admin is not tied to any school
            )
            
            db.session.add(super_admin)
            db.session.commit()
            
            print("✅ Super admin account created successfully!")
            print(f"Username: superadmin")
            print(f"Password: {super_admin_password}")
            print(f"Email: superadmin@edutrack.com")
            print(f"Role: super_admin")
            print("\nYou can now login at: http://127.0.0.1:5000/login")
            print("Then access the super admin dashboard at: http://127.0.0.1:5000/super-admin")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating super admin: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    print("Creating Super Admin Account for EduTrack...")
    print("=" * 50)
    
    success = create_super_admin()
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 Super admin account is ready!")
        print("Login credentials:")
        print("  Username: superadmin")
        print("  Password: superadmin123")
    else:
        print("\n" + "=" * 50)
        print("❌ Failed to create super admin account")
        sys.exit(1)
