#!/usr/bin/env python3
"""
Aiven Database Setup Script for Student Assignment Tracking App
Creates database tables and initializes the application with Aiven cloud database
"""

import os
import sys
from dotenv import load_dotenv
from urllib.parse import urlparse

# Add the current directory to Python path to import from app.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db

def setup_aiven_database():
    """Setup database tables in Aiven cloud database"""
    print("🚀 Setting up Aiven database for Student Assignment Tracking App...")
    
    # Load environment variables
    load_dotenv()
    
    # Check if DATABASE_URL is set
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ Error: DATABASE_URL not found in environment variables")
        print("Please set DATABASE_URL in your .env file or environment")
        print("Example: DATABASE_URL=postgresql://user:pass@host:port/dbname")
        sys.exit(1)
    
    # Parse database URL to show connection details
    parsed_url = urlparse(database_url)
    print(f"📊 Database Type: {parsed_url.scheme.upper()}")
    print(f"🏠 Host: {parsed_url.hostname}")
    print(f"🔌 Port: {parsed_url.port}")
    print(f"📁 Database: {parsed_url.path[1:]}")
    print(f"👤 User: {parsed_url.username}")
    print("-" * 50)
    
    try:
        # Create all tables
        with app.app_context():
            print("🔄 Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Check if we need to create initial admin user
            from app import User
            admin_user = User.query.filter_by(username='admin').first()
            
            if not admin_user:
                print("👤 Creating default admin user...")
                admin_user = User(
                    username='admin',
                    email='admin@school.com',
                    password_hash=User.hash_password('admin123'),
                    role='admin',
                    first_name='Admin',
                    last_name='User'
                )
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Default admin user created!")
                print("   Username: admin")
                print("   Password: admin123")
                print("   ⚠️  Please change the default password after first login!")
            else:
                print("ℹ️  Admin user already exists")
            
            # Display table information
            print("\n📋 Database Tables Created:")
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            for table in sorted(tables):
                columns = inspector.get_columns(table)
                print(f"  • {table} ({len(columns)} columns)")
            
            print(f"\n✅ Aiven database setup completed successfully!")
            print(f"🌐 Your application is ready to use with Aiven cloud database")
            
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your DATABASE_URL in .env file")
        print("2. Ensure your Aiven database is running")
        print("3. Verify network connectivity to Aiven")
        print("4. Check database credentials and permissions")
        sys.exit(1)

def test_connection():
    """Test database connection"""
    print("🔍 Testing database connection...")
    
    try:
        with app.app_context():
            # Simple query to test connection
            result = db.session.execute(db.text("SELECT 1")).fetchone()
            if result:
                print("✅ Database connection successful!")
                return True
            else:
                print("❌ Database connection failed!")
                return False
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Setup Aiven database for Student Assignment Tracking App')
    parser.add_argument('--test-only', action='store_true',
                       help='Only test database connection')
    parser.add_argument('--force', action='store_true',
                       help='Force recreate all tables (WARNING: This will delete existing data)')
    
    args = parser.parse_args()
    
    if args.test_only:
        if test_connection():
            print("🎉 Database is ready!")
        else:
            print("💥 Database connection failed!")
            sys.exit(1)
    else:
        if args.force:
            print("⚠️  WARNING: Force mode enabled - this will delete existing data!")
            response = input("Are you sure you want to continue? (yes/no): ")
            if response.lower() != 'yes':
                print("❌ Operation cancelled")
                sys.exit(0)
        
        # Test connection first
        if not test_connection():
            print("💥 Cannot proceed - database connection failed!")
            sys.exit(1)
        
        # Setup database
        setup_aiven_database()

if __name__ == '__main__':
    main()
