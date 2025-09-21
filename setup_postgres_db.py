#!/usr/bin/env python3
"""
Setup PostgreSQL Database for Student Assignment Tracking App
Creates all necessary tables in the Aiven PostgreSQL database
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('aiven_config.env')

# Add the current directory to Python path to import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db

def create_tables():
    """Create all database tables"""
    print("🚀 Setting up PostgreSQL database tables...")
    print(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print("-" * 50)
    
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✅ All database tables created successfully!")
            
            # List all tables
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"\n📋 Created tables ({len(tables)}):")
            for table in sorted(tables):
                print(f"  - {table}")
            
            print("\n🎉 Database setup completed successfully!")
            print("🔧 You can now run the migration script to transfer data from SQLite")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        sys.exit(1)

def verify_connection():
    """Verify database connection"""
    print("🔍 Verifying database connection...")
    
    try:
        with app.app_context():
            # Test connection using modern SQLAlchemy syntax
            with db.engine.connect() as connection:
                connection.execute(db.text("SELECT 1"))
            print("✅ Database connection successful!")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Main function"""
    print("Student Assignment Tracking App - PostgreSQL Setup")
    print("=" * 50)
    
    # Verify connection first
    if not verify_connection():
        print("\n❌ Cannot proceed without database connection")
        sys.exit(1)
    
    # Create tables
    create_tables()

if __name__ == '__main__':
    main()
