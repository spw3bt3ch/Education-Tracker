#!/usr/bin/env python3
"""
Update Email Configuration Script
"""

import os
import shutil
from datetime import datetime

def backup_config():
    """Backup current configuration"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"aiven_config_backup_{timestamp}.env"
    shutil.copy2("aiven_config.env", backup_file)
    print(f"✅ Configuration backed up to: {backup_file}")
    return backup_file

def update_email_config():
    """Update email configuration"""
    print("🔧 Email Configuration Update Tool")
    print("=" * 50)
    
    # Backup current config
    backup_file = backup_config()
    
    print("\n📧 Current Email Configuration:")
    print(f"MAIL_USERNAME: {os.getenv('MAIL_USERNAME')}")
    print(f"MAIL_PASSWORD: {'*' * len(os.getenv('MAIL_PASSWORD', ''))}")
    
    print("\n🔑 To fix the email issue, you need to:")
    print("1. Go to https://myaccount.google.com/")
    print("2. Security → 2-Step Verification (enable if not already)")
    print("3. App passwords → Generate app password")
    print("4. Select 'Mail' and 'Other (custom name)'")
    print("5. Enter 'EduTrack' as the name")
    print("6. Copy the 16-character password")
    
    print("\n📝 The password should look like: 'abcd efgh ijkl mnop'")
    print("   (16 characters with spaces)")
    
    # Get new password from user
    new_password = input("\n🔑 Enter your new Gmail App Password: ").strip()
    
    if len(new_password) != 16 or not all(c.isalnum() or c.isspace() for c in new_password):
        print("❌ Invalid password format! Please try again.")
        return False
    
    # Update configuration
    try:
        with open("aiven_config.env", "r") as f:
            lines = f.readlines()
        
        # Update MAIL_PASSWORD
        updated_lines = []
        for line in lines:
            if line.startswith("MAIL_PASSWORD="):
                updated_lines.append(f"MAIL_PASSWORD={new_password}\n")
            else:
                updated_lines.append(line)
        
        # Write updated configuration
        with open("aiven_config.env", "w") as f:
            f.writelines(updated_lines)
        
        print("✅ Email configuration updated successfully!")
        print("📧 You can now test the email functionality")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating configuration: {str(e)}")
        return False

if __name__ == "__main__":
    update_email_config()
