#!/usr/bin/env python3
"""
Comprehensive Email Debug Script
"""

import os
import sys
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

# Load environment variables
load_dotenv('aiven_config.env')

def test_direct_smtp():
    """Test SMTP connection directly"""
    print("🔍 Testing Direct SMTP Connection...")
    
    try:
        smtp_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('MAIL_PORT', 587))
        username = os.getenv('MAIL_USERNAME')
        password = os.getenv('MAIL_PASSWORD')
        
        print(f"SMTP Server: {smtp_server}")
        print(f"SMTP Port: {smtp_port}")
        print(f"Username: {username}")
        print(f"Password: {'*' * len(password) if password else 'NOT SET'}")
        
        # Test connection
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(username, password)
        
        # Send test email
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = username  # Send to self
        msg['Subject'] = "EduTrack Direct SMTP Test"
        
        body = f"""
        This is a direct SMTP test email from EduTrack.
        
        Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}
        SMTP Server: {smtp_server}
        Port: {smtp_port}
        
        If you receive this email, your SMTP configuration is working correctly.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        text = msg.as_string()
        server.sendmail(username, username, text)
        server.quit()
        
        print("✅ Direct SMTP test successful!")
        print("📧 Check your email inbox for the test email")
        return True
        
    except Exception as e:
        print(f"❌ Direct SMTP test failed: {str(e)}")
        return False

def test_flask_mail_sync():
    """Test Flask-Mail synchronously"""
    print("\n🔍 Testing Flask-Mail Synchronously...")
    
    try:
        from flask import Flask
        from flask_mail import Mail, Message
        
        # Create Flask app
        app = Flask(__name__)
        app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
        app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
        app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
        app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
        app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
        app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
        app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
        
        # Initialize Flask-Mail
        mail = Mail(app)
        
        with app.app_context():
            # Send test email synchronously
            msg = Message(
                subject="EduTrack Flask-Mail Sync Test",
                recipients=[os.getenv('MAIL_DEFAULT_SENDER')],
                sender=os.getenv('MAIL_DEFAULT_SENDER'),
                body=f"""
                This is a synchronous Flask-Mail test email from EduTrack.
                
                Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}
                
                If you receive this email, Flask-Mail is working correctly.
                """
            )
            
            mail.send(msg)
            print("✅ Flask-Mail sync test successful!")
            print("📧 Check your email inbox for the test email")
            return True
            
    except Exception as e:
        print(f"❌ Flask-Mail sync test failed: {str(e)}")
        return False

def test_app_password_reset():
    """Test the actual password reset functionality"""
    print("\n🔍 Testing App Password Reset Functionality...")
    
    try:
        # Add current directory to Python path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from app import app, db, User, EmailService
        
        with app.app_context():
            # Create a test user
            test_user = User(
                username='testuser123',
                email=os.getenv('MAIL_DEFAULT_SENDER'),  # Use your email
                password_hash='test_hash',
                role='teacher',
                first_name='Test',
                last_name='User',
                school_id=1
            )
            
            # Test password reset email
            result = EmailService.send_password_reset_email(
                test_user, 
                'test_token_123', 
                'testpassword123'
            )
            
            if result:
                print("✅ App password reset email sent successfully!")
                print("📧 Check your email inbox for the password reset email")
                return True
            else:
                print("❌ App password reset email failed!")
                return False
                
    except Exception as e:
        print(f"❌ App password reset test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_gmail_settings():
    """Check Gmail-specific settings"""
    print("\n🔍 Checking Gmail Settings...")
    
    password = os.getenv('MAIL_PASSWORD')
    username = os.getenv('MAIL_USERNAME')
    
    print(f"Gmail Address: {username}")
    print(f"App Password: {'*' * len(password) if password else 'NOT SET'}")
    
    if not password:
        print("❌ MAIL_PASSWORD not set!")
        return False
    
    if len(password) != 16 or not all(c.isalnum() or c.isspace() for c in password):
        print("❌ MAIL_PASSWORD doesn't look like a Gmail App Password!")
        print("   Gmail App Passwords should be 16 characters with spaces")
        print("   Example: 'abcd efgh ijkl mnop'")
        return False
    
    print("✅ Gmail App Password format looks correct")
    return True

def main():
    """Main function"""
    print("🚀 EduTrack Email Debug Script - Comprehensive Test")
    print("=" * 60)
    
    # Check Gmail settings
    gmail_ok = check_gmail_settings()
    
    # Test direct SMTP
    smtp_ok = test_direct_smtp()
    
    # Test Flask-Mail sync
    flask_ok = test_flask_mail_sync()
    
    # Test app functionality
    app_ok = test_app_password_reset()
    
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST RESULTS:")
    print(f"Gmail Settings: {'✅ PASS' if gmail_ok else '❌ FAIL'}")
    print(f"Direct SMTP: {'✅ PASS' if smtp_ok else '❌ FAIL'}")
    print(f"Flask-Mail Sync: {'✅ PASS' if flask_ok else '❌ FAIL'}")
    print(f"App Password Reset: {'✅ PASS' if app_ok else '❌ FAIL'}")
    
    print("\n💡 TROUBLESHOOTING TIPS:")
    print("1. Check your email SPAM/JUNK folder")
    print("2. Wait 2-3 minutes for emails to arrive")
    print("3. Make sure you're using a Gmail App Password, not your regular password")
    print("4. Verify 2-Factor Authentication is enabled on your Gmail account")
    print("5. Check if Gmail is blocking the connection (check Gmail security settings)")
    
    if all([gmail_ok, smtp_ok, flask_ok, app_ok]):
        print("\n🎉 All tests passed! Emails should be working.")
    else:
        print("\n⚠️  Some tests failed. Please check the configuration.")

if __name__ == "__main__":
    main()
