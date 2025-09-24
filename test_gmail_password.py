#!/usr/bin/env python3
"""
Test Gmail App Password
"""

import smtplib
from email.mime.text import MIMEText

def test_gmail_connection():
    """Test Gmail connection with current password"""
    print("🔍 Testing Gmail Connection...")
    
    # Your current configuration
    username = "samueloluwapelumi8@gmail.com"
    password = "ohyl cyzw mnot dnte"  # Your new password
    
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Password length: {len(password)}")
    print(f"Password format: {'✅ Correct' if len(password) == 16 and ' ' in password else '❌ Incorrect'}")
    
    try:
        # Test connection
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(username, password)
        
        # Send test email
        msg = MIMEText("This is a test email from EduTrack.")
        msg['Subject'] = "EduTrack Test Email"
        msg['From'] = username
        msg['To'] = username
        
        server.sendmail(username, username, msg.as_string())
        server.quit()
        
        print("✅ Gmail connection successful!")
        print("📧 Test email sent! Check your inbox.")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("\n🔧 SOLUTION:")
        print("1. Go to https://myaccount.google.com/")
        print("2. Security → 2-Step Verification (enable if not already)")
        print("3. App passwords → Generate app password")
        print("4. Select 'Mail' and 'Other (custom name)'")
        print("5. Enter 'EduTrack' as the name")
        print("6. Copy the NEW 16-character password")
        print("7. Update your aiven_config.env file with the new password")
        return False
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_gmail_connection()
