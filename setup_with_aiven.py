#!/usr/bin/env python3
"""
Quick Setup Script for Student Assignment Tracking App with Aiven Database
Configures the application with your specific Aiven database details
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

def print_banner():
    """Print setup banner"""
    print("=" * 70)
    print("🎓 Student Assignment Tracking App - Aiven Setup")
    print("=" * 70)
    print("Setting up with your Aiven PostgreSQL database...")
    print()

def create_env_file():
    """Create .env file with Aiven configuration"""
    print("🔧 Creating .env configuration file...")
    
    env_content = """# Aiven Database Configuration
DATABASE_URL=postgres://avnadmin:AVNS_QtoIA0l1WvEV4I565Kj@pg-6e8de0c-smiwebsolutions08-5612.c.aivencloud.com:27725/defaultdb?sslmode=require

# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=production

# Aiven Database Details (for reference)
AIVEN_DB_HOST=pg-6e8de0c-smiwebsolutions08-5612.c.aivencloud.com
AIVEN_DB_PORT=27725
AIVEN_DB_NAME=defaultdb
AIVEN_DB_USER=avnadmin
AIVEN_DB_PASSWORD=AVNS_QtoIA0l1WvEV4I565Kj
AIVEN_DB_SSL_MODE=require
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env file created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True, text=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def test_database_connection():
    """Test connection to Aiven database"""
    print("🔍 Testing database connection...")
    
    try:
        # Load environment variables
        load_dotenv()
        
        # Test connection using setup script
        result = subprocess.run([sys.executable, 'setup_aiven.py', '--test-only'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Database connection successful!")
            return True
        else:
            print(f"❌ Database connection failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False

def setup_database_tables():
    """Set up database tables in Aiven"""
    print("🏗️  Setting up database tables...")
    
    try:
        result = subprocess.run([sys.executable, 'setup_aiven.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Database tables created successfully!")
            return True
        else:
            print(f"❌ Error setting up tables: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False

def migrate_data():
    """Migrate data from SQLite to Aiven"""
    print("📤 Migrating data from SQLite to Aiven...")
    
    # Check if SQLite database exists
    if not os.path.exists('instance/edutrack.db'):
        print("⚠️  No SQLite database found. Skipping data migration.")
        print("   You can add data manually through the application.")
        return True
    
    try:
        # Export data from SQLite
        print("  📤 Exporting data from SQLite...")
        export_result = subprocess.run([sys.executable, 'migrate_to_aiven.py', '--export-only'], 
                                     capture_output=True, text=True)
        
        if export_result.returncode != 0:
            print(f"❌ Export failed: {export_result.stderr}")
            return False
        
        # Import data to Aiven
        print("  📥 Importing data to Aiven...")
        import_result = subprocess.run([sys.executable, 'migrate_to_aiven.py', '--import-only', '--target', 'postgres'], 
                                     capture_output=True, text=True)
        
        if import_result.returncode == 0:
            print("✅ Data migrated successfully!")
            return True
        else:
            print(f"❌ Import failed: {import_result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error migrating data: {e}")
        return False

def test_application():
    """Test if application starts correctly"""
    print("🧪 Testing application startup...")
    
    try:
        # Test if we can import the app
        from app import app, db
        
        with app.app_context():
            # Test database query
            result = db.session.execute(db.text("SELECT 1")).fetchone()
            if result:
                print("✅ Application test successful!")
                return True
            else:
                print("❌ Application test failed")
                return False
                
    except Exception as e:
        print(f"❌ Application test error: {e}")
        return False

def main():
    """Main setup function"""
    print_banner()
    
    print("🚀 Starting setup with your Aiven database...")
    print("   Host: pg-6e8de0c-smiwebsolutions08-5612.c.aivencloud.com")
    print("   Port: 27725")
    print("   Database: defaultdb")
    print("   User: avnadmin")
    print()
    
    # Step 1: Create .env file
    if not create_env_file():
        print("💥 Setup failed at configuration step")
        sys.exit(1)
    
    # Step 2: Install dependencies
    if not install_dependencies():
        print("💥 Setup failed at dependency installation")
        sys.exit(1)
    
    # Step 3: Test database connection
    if not test_database_connection():
        print("💥 Setup failed at database connection test")
        print("   Please check your Aiven database is running and accessible")
        sys.exit(1)
    
    # Step 4: Setup database tables
    if not setup_database_tables():
        print("💥 Setup failed at database table creation")
        sys.exit(1)
    
    # Step 5: Migrate data (if SQLite exists)
    if not migrate_data():
        print("⚠️  Data migration failed, but you can continue without existing data")
    
    # Step 6: Test application
    if not test_application():
        print("💥 Setup failed at application test")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("🎉 Setup completed successfully!")
    print("="*70)
    print()
    print("✅ Your Student Assignment Tracking App is now configured with Aiven!")
    print()
    print("🚀 Next steps:")
    print("   1. Start your application: python app.py")
    print("   2. Open your browser to: http://localhost:5000")
    print("   3. Login with admin credentials:")
    print("      Username: admin")
    print("      Password: admin123")
    print()
    print("🔧 Configuration details:")
    print("   • Database: Aiven PostgreSQL")
    print("   • Host: pg-6e8de0c-smiwebsolutions08-5612.c.aivencloud.com")
    print("   • Port: 27725")
    print("   • Database: defaultdb")
    print()
    print("📚 For more information, see AIVEN_MIGRATION_GUIDE.md")

if __name__ == '__main__':
    main()
