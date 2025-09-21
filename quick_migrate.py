#!/usr/bin/env python3
"""
Quick Migration Script for Student Assignment Tracking App
Simplified migration to Aiven cloud database
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

def print_banner():
    """Print welcome banner"""
    print("=" * 60)
    print("🚀 Student Assignment Tracking App - Aiven Migration")
    print("=" * 60)
    print()

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required")
        return False
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("   Please copy config.env.example to .env and configure it")
        return False
    
    # Check if SQLite database exists
    if not os.path.exists('instance/edutrack.db'):
        print("❌ SQLite database not found at instance/edutrack.db")
        return False
    
    # Check if required packages are installed
    try:
        import psycopg2
        import pymysql
        from dotenv import load_dotenv
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    print("✅ All requirements met!")
    return True

def get_database_choice():
    """Get user's database choice"""
    print("\n📊 Choose your Aiven database type:")
    print("1. PostgreSQL (Recommended)")
    print("2. MySQL")
    
    while True:
        choice = input("\nEnter your choice (1 or 2): ").strip()
        if choice == '1':
            return 'postgres'
        elif choice == '2':
            return 'mysql'
        else:
            print("❌ Invalid choice. Please enter 1 or 2.")

def check_database_url():
    """Check if DATABASE_URL is configured"""
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found in .env file")
        print("   Please configure your Aiven database URL in .env file")
        return False
    
    if database_url.startswith('sqlite'):
        print("❌ DATABASE_URL is still pointing to SQLite")
        print("   Please update DATABASE_URL in .env file with your Aiven connection string")
        return False
    
    print("✅ DATABASE_URL configured")
    return True

def run_migration(database_type):
    """Run the migration process"""
    print(f"\n🔄 Starting migration to {database_type.upper()}...")
    
    try:
        # Step 1: Export data
        print("\n📤 Step 1: Exporting data from SQLite...")
        result = subprocess.run([
            sys.executable, 'migrate_to_aiven.py', 
            '--export-only'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Export failed: {result.stderr}")
            return False
        
        print("✅ Data exported successfully")
        
        # Step 2: Setup database
        print(f"\n🏗️  Step 2: Setting up {database_type.upper()} database...")
        result = subprocess.run([
            sys.executable, 'setup_aiven.py'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Database setup failed: {result.stderr}")
            return False
        
        print("✅ Database setup completed")
        
        # Step 3: Import data
        print(f"\n📥 Step 3: Importing data to {database_type.upper()}...")
        result = subprocess.run([
            sys.executable, 'migrate_to_aiven.py',
            '--import-only', '--target', database_type
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Import failed: {result.stderr}")
            return False
        
        print("✅ Data imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False

def test_application():
    """Test if application works with new database"""
    print("\n🧪 Testing application...")
    
    try:
        # Test database connection
        result = subprocess.run([
            sys.executable, 'setup_aiven.py', '--test-only'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Database test failed: {result.stderr}")
            return False
        
        print("✅ Database connection test passed")
        return True
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    """Main migration function"""
    print_banner()
    
    # Check requirements
    if not check_requirements():
        print("\n💥 Migration cannot proceed. Please fix the issues above.")
        sys.exit(1)
    
    # Check database URL
    if not check_database_url():
        print("\n💥 Please configure your DATABASE_URL in .env file first.")
        print("   See AIVEN_MIGRATION_GUIDE.md for details.")
        sys.exit(1)
    
    # Get database choice
    database_type = get_database_choice()
    
    # Confirm migration
    print(f"\n⚠️  WARNING: This will migrate your data to Aiven {database_type.upper()}")
    print("   Make sure you have:")
    print("   1. Backed up your current data")
    print("   2. Configured your Aiven database")
    print("   3. Updated DATABASE_URL in .env file")
    
    confirm = input("\nDo you want to continue? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("❌ Migration cancelled")
        sys.exit(0)
    
    # Run migration
    if run_migration(database_type):
        print("\n🎉 Migration completed successfully!")
        
        # Test application
        if test_application():
            print("\n✅ Application is ready to use with Aiven database!")
            print("\n🚀 Next steps:")
            print("   1. Start your application: python app.py")
            print("   2. Test all functionality")
            print("   3. Update your deployment configuration")
            print("   4. Consider backing up your old SQLite database")
        else:
            print("\n⚠️  Migration completed but application test failed")
            print("   Please check the troubleshooting guide")
    else:
        print("\n💥 Migration failed!")
        print("   Please check the error messages above and try again")
        print("   See AIVEN_MIGRATION_GUIDE.md for detailed instructions")
        sys.exit(1)

if __name__ == '__main__':
    main()
