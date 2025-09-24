#!/usr/bin/env python3
"""
Secure Setup Script for SMIED with Aiven Database
Prompts for sensitive information and creates secure configuration
"""

import os
import sys
import getpass
import secrets
from dotenv import load_dotenv

def print_banner():
    """Print setup banner"""
    print("=" * 70)
    print("🔒 SMIED - Secure Setup with Aiven Database")
    print("=" * 70)
    print("This script will help you securely configure SMIED with your Aiven database.")
    print("All sensitive information will be stored in environment variables.")
    print()

def get_secure_input(prompt, is_password=False):
    """Get secure input from user"""
    if is_password:
        return getpass.getpass(prompt)
    else:
        return input(prompt)

def generate_secret_key():
    """Generate a secure secret key"""
    return secrets.token_hex(32)

def get_database_config():
    """Get database configuration from user input"""
    print("📊 Database Configuration")
    print("-" * 30)
    
    config = {}
    
    # Get database host
    config['host'] = get_secure_input("Aiven Database Host: ")
    if not config['host']:
        print("❌ Database host is required")
        return None
    
    # Get database port
    port_input = get_secure_input("Aiven Database Port (default: 27725): ")
    config['port'] = port_input if port_input else "27725"
    
    # Get database name
    config['database'] = get_secure_input("Aiven Database Name: ")
    if not config['database']:
        print("❌ Database name is required")
        return None
    
    # Get database user
    config['user'] = get_secure_input("Aiven Database User (default: avnadmin): ")
    config['user'] = config['user'] if config['user'] else "avnadmin"
    
    # Get database password
    config['password'] = get_secure_input("Aiven Database Password: ", is_password=True)
    if not config['password']:
        print("❌ Database password is required")
        return None
    
    # Get SSL mode
    ssl_input = get_secure_input("SSL Mode (default: require): ")
    config['ssl_mode'] = ssl_input if ssl_input else "require"
    
    # Construct DATABASE_URL
    config['database_url'] = f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?sslmode={config['ssl_mode']}"
    
    return config

def get_email_config():
    """Get email configuration from user input"""
    print("\n📧 Email Configuration")
    print("-" * 30)
    
    config = {}
    
    # Get email server
    config['server'] = get_secure_input("SMTP Server (default: smtp.gmail.com): ")
    config['server'] = config['server'] if config['server'] else "smtp.gmail.com"
    
    # Get email port
    port_input = get_secure_input("SMTP Port (default: 587): ")
    config['port'] = port_input if port_input else "587"
    
    # Get email username
    config['username'] = get_secure_input("Email Username: ")
    if not config['username']:
        print("⚠️  Email username not provided, email features will be disabled")
    
    # Get email password
    config['password'] = get_secure_input("Email Password/App Password: ", is_password=True)
    if not config['password']:
        print("⚠️  Email password not provided, email features will be disabled")
    
    # Get default sender
    config['sender'] = get_secure_input("Default Sender Email: ")
    if not config['sender']:
        config['sender'] = config['username']
    
    return config

def get_payment_config():
    """Get payment configuration from user input"""
    print("\n💳 Payment Configuration (Paystack)")
    print("-" * 30)
    
    config = {}
    
    # Get Paystack public key
    config['public_key'] = get_secure_input("Paystack Public Key: ")
    if not config['public_key']:
        print("⚠️  Paystack public key not provided, payment features will be disabled")
    
    # Get Paystack secret key
    config['secret_key'] = get_secure_input("Paystack Secret Key: ", is_password=True)
    if not config['secret_key']:
        print("⚠️  Paystack secret key not provided, payment features will be disabled")
    
    # Get webhook secret
    config['webhook_secret'] = get_secure_input("Paystack Webhook Secret: ", is_password=True)
    if not config['webhook_secret']:
        print("⚠️  Webhook secret not provided, webhook features will be disabled")
    
    return config

def get_user_passwords():
    """Get default user passwords"""
    print("\n👥 Default User Passwords")
    print("-" * 30)
    print("Enter passwords for default users (or press Enter for defaults)")
    
    config = {}
    
    # Get super admin password
    super_admin_pwd = get_secure_input("Super Admin Password (default: superadmin123): ", is_password=True)
    config['super_admin'] = super_admin_pwd if super_admin_pwd else "superadmin123"
    
    # Get admin password
    admin_pwd = get_secure_input("School Admin Password (default: admin123): ", is_password=True)
    config['admin'] = admin_pwd if admin_pwd else "admin123"
    
    # Get teacher password
    teacher_pwd = get_secure_input("Teacher Password (default: teacher123): ", is_password=True)
    config['teacher'] = teacher_pwd if teacher_pwd else "teacher123"
    
    # Get parent password
    parent_pwd = get_secure_input("Parent Password (default: parent123): ", is_password=True)
    config['parent'] = parent_pwd if parent_pwd else "parent123"
    
    return config

def create_env_file(database_config, email_config, payment_config, user_passwords):
    """Create .env file with all configuration"""
    print("\n🔧 Creating .env configuration file...")
    
    # Generate secret key
    secret_key = generate_secret_key()
    
    env_content = f"""# SMIED Environment Configuration
# This file contains sensitive data and should not be committed to version control

# Database Configuration
DATABASE_URL={database_config['database_url']}

# Flask Configuration
SECRET_KEY={secret_key}
FLASK_ENV=production

# Default User Passwords
SUPER_ADMIN_PASSWORD={user_passwords['super_admin']}
ADMIN_PASSWORD={user_passwords['admin']}
TEACHER_PASSWORD={user_passwords['teacher']}
PARENT_PASSWORD={user_passwords['parent']}

# Email Configuration
MAIL_SERVER={email_config['server']}
MAIL_PORT={email_config['port']}
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME={email_config['username']}
MAIL_PASSWORD={email_config['password']}
MAIL_DEFAULT_SENDER={email_config['sender']}
MAIL_MAX_EMAILS=100
MAIL_SUPPRESS_SEND=False

# Paystack Payment Configuration
PAYSTACK_PUBLIC_KEY={payment_config['public_key']}
PAYSTACK_SECRET_KEY={payment_config['secret_key']}
PAYSTACK_WEBHOOK_SECRET={payment_config['webhook_secret']}

# Aiven Database Details (for reference)
AIVEN_DB_HOST={database_config['host']}
AIVEN_DB_PORT={database_config['port']}
AIVEN_DB_NAME={database_config['database']}
AIVEN_DB_USER={database_config['user']}
AIVEN_DB_PASSWORD={database_config['password']}
AIVEN_DB_SSL_MODE={database_config['ssl_mode']}
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env file created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def main():
    """Main setup function"""
    print_banner()
    
    # Check if .env already exists
    if os.path.exists('.env'):
        overwrite = input("⚠️  .env file already exists. Overwrite? (y/N): ")
        if overwrite.lower() != 'y':
            print("Setup cancelled.")
            sys.exit(0)
    
    try:
        # Get all configuration
        database_config = get_database_config()
        if not database_config:
            print("💥 Setup failed: Database configuration required")
            sys.exit(1)
        
        email_config = get_email_config()
        payment_config = get_payment_config()
        user_passwords = get_user_passwords()
        
        # Create .env file
        if not create_env_file(database_config, email_config, payment_config, user_passwords):
            print("💥 Setup failed: Could not create .env file")
            sys.exit(1)
        
        print("\n" + "="*70)
        print("🎉 Secure setup completed successfully!")
        print("="*70)
        print()
        print("✅ SMIED is now configured with your Aiven database!")
        print()
        print("🔒 Security features:")
        print("   • All sensitive data stored in .env file")
        print("   • Strong secret key generated")
        print("   • Passwords not displayed in terminal")
        print("   • .env file excluded from version control")
        print()
        print("🚀 Next steps:")
        print("   1. Start your application: python app.py")
        print("   2. Open your browser to: http://localhost:5000")
        print("   3. Login with your configured credentials")
        print()
        print("📚 For more information, see SETUP.md")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Setup failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
