#!/usr/bin/env python3
"""
Setup script for Render PostgreSQL database
This script helps initialize the database and set up the application
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def load_configuration():
    """Load database configuration"""
    if os.path.exists('render_config.env'):
        load_dotenv('render_config.env')
        print("✅ Loaded configuration from render_config.env")
    elif os.path.exists('.env'):
        load_dotenv('.env')
        print("✅ Loaded configuration from .env")
    else:
        print("❌ No configuration file found")
        return None
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return None
    
    return database_url

def test_connection(database_url):
    """Test database connection"""
    try:
        engine = create_engine(database_url, echo=False)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Database connection successful!")
            print(f"📊 PostgreSQL version: {version}")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def create_tables(database_url):
    """Create database tables using Flask-SQLAlchemy"""
    try:
        print("🔧 Creating database tables...")
        
        # Import Flask app and models
        from app import app, db
        
        # Create all tables
        with app.app_context():
            db.create_all()
            print("✅ Database tables created successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False

def show_next_steps():
    """Show next steps for the user"""
    print("\n" + "=" * 60)
    print("🎉 Render PostgreSQL Database Setup Complete!")
    print("=" * 60)
    print("\n📋 Configuration Summary:")
    print("• Database: Render Cloud PostgreSQL")
    print("• Host: dpg-d3ru3eripnbc738jkja0-a.oregon-postgres.render.com")
    print("• Database Name: smied_db")
    print("• Username: smied_db_user")
    print("\n🚀 Next Steps:")
    print("1. Run your Flask application: python app.py")
    print("2. If you have existing data, run: python migrate_to_render_db.py")
    print("3. Test all functionality to ensure everything works")
    print("4. Update your deployment configuration if needed")
    print("\n💡 Tips:")
    print("• Your app will now use PostgreSQL instead of SQLite")
    print("• Make sure to update your deployment environment variables")
    print("• Consider setting up database backups")
    print("• Monitor your database usage on Render dashboard")

def main():
    """Main setup function"""
    print("🚀 Setting up Render PostgreSQL Database")
    print("=" * 50)
    
    # Load configuration
    database_url = load_configuration()
    if not database_url:
        print("❌ Failed to load configuration")
        return False
    
    # Test connection
    print("\n🔗 Testing database connection...")
    if not test_connection(database_url):
        return False
    
    # Create tables
    print("\n🔧 Setting up database schema...")
    if not create_tables(database_url):
        return False
    
    # Show next steps
    show_next_steps()
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
