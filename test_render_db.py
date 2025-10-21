#!/usr/bin/env python3
"""
Test script to verify Render PostgreSQL database connection
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, DisconnectionError
from dotenv import load_dotenv

def test_database_connection():
    """Test the database connection with the new Render PostgreSQL configuration"""
    
    # Load environment variables
    if os.path.exists('render_config.env'):
        load_dotenv('render_config.env')
        print("✅ Loaded configuration from render_config.env")
    elif os.path.exists('.env'):
        load_dotenv('.env')
        print("✅ Loaded configuration from .env")
    else:
        print("⚠️  No configuration file found")
        return False
    
    # Get database URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    print(f"🔗 Testing connection to: {database_url.split('@')[1] if '@' in database_url else 'database'}")
    
    try:
        # Create engine
        engine = create_engine(database_url, echo=False)
        
        # Test connection
        with engine.connect() as connection:
            # Execute a simple query
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Database connection successful!")
            print(f"📊 PostgreSQL version: {version}")
            
            # Test if we can create a simple table (optional)
            try:
                connection.execute(text("""
                    CREATE TABLE IF NOT EXISTS test_connection (
                        id SERIAL PRIMARY KEY,
                        test_data VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """))
                print("✅ Test table creation successful")
                
                # Clean up test table
                connection.execute(text("DROP TABLE IF EXISTS test_connection;"))
                print("✅ Test table cleanup successful")
                
            except Exception as e:
                print(f"⚠️  Test table operations failed: {e}")
            
            return True
            
    except OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        return False
    except DisconnectionError as e:
        print(f"❌ Database disconnection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def show_connection_details():
    """Display connection details for verification"""
    print("\n📋 Database Connection Details:")
    print("=" * 50)
    print(f"Hostname: dpg-d3ru3eripnbc738jkja0-a.oregon-postgres.render.com")
    print(f"Port: 5432")
    print(f"Database: smied_db")
    print(f"Username: smied_db_user")
    print(f"Password: [HIDDEN]")
    print(f"Internal URL: postgresql://smied_db_user:***@dpg-d3ru3eripnbc738jkja0-a/smied_db")
    print(f"External URL: postgresql://smied_db_user:***@dpg-d3ru3eripnbc738jkja0-a.oregon-postgres.render.com/smied_db")
    print("=" * 50)

if __name__ == "__main__":
    print("🚀 Testing Render PostgreSQL Database Connection")
    print("=" * 60)
    
    show_connection_details()
    
    if test_database_connection():
        print("\n🎉 Database configuration is working correctly!")
        print("✅ You can now run your Flask application with the new database.")
    else:
        print("\n❌ Database connection failed!")
        print("Please check your configuration and try again.")
        sys.exit(1)
