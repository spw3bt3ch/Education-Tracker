#!/usr/bin/env python3
"""
Send a test welcome email to verify the email system is working
"""

import os
from dotenv import load_dotenv
from app import app, db, User, School, EmailService

def send_test_welcome_email():
    """Send a test welcome email"""
    load_dotenv('aiven_config.env')
    
    with app.app_context():
        try:
            # Get or create a test school
            school = School.query.first()
            if not school:
                school = School(
                    name="Test School",
                    code="TEST01",
                    address="123 Test Street",
                    email="test@school.com"
                )
                db.session.add(school)
                db.session.commit()
            
            # Create a test user
            test_user = User(
                username="testuser",
                email=os.getenv('MAIL_DEFAULT_SENDER'),  # Send to your own email
                password_hash="test",
                role="teacher",
                first_name="Test",
                last_name="User",
                school_id=school.id
            )
            
            print("Sending test welcome email...")
            print(f"To: {test_user.email}")
            print(f"School: {school.name}")
            
            # Send welcome email
            success = EmailService.send_welcome_email(test_user, school)
            
            if success:
                print("✅ Test welcome email sent successfully!")
                print("Check your inbox for the welcome email.")
            else:
                print("❌ Failed to send test welcome email.")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    send_test_welcome_email()
