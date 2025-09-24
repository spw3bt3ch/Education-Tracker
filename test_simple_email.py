#!/usr/bin/env python3
"""
Simple Email Test - Send a basic email to verify delivery
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv('aiven_config.env')

def send_simple_email():
    """Send a simple test email"""
    print("📧 Sending Simple Test Email...")
    
    try:
        # Email configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        username = os.getenv('MAIL_USERNAME')
        password = os.getenv('MAIL_PASSWORD')
        
        print(f"From: {username}")
        print(f"To: {username}")
        print(f"Password: {'*' * len(password) if password else 'NOT SET'}")
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = username
        msg['Subject'] = f"EduTrack Test Email - {time.strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Email body
        body = f"""
        Hello!
        
        This is a test email from EduTrack to verify email functionality.
        
        Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}
        
        If you receive this email, your email configuration is working correctly.
        
        Best regards,
        EduTrack System
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(username, password)
        
        text = msg.as_string()
        server.sendmail(username, username, text)
        server.quit()
        
        print("✅ Email sent successfully!")
        print("📧 Please check your email inbox (including spam folder)")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Simple Email Test")
    print("=" * 40)
    send_simple_email()
