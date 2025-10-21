#!/usr/bin/env python3
"""
Migration script to transfer data from SQLite to Render PostgreSQL database
"""

import os
import sys
from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import sqlite3
from datetime import datetime

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
        return None, None
    
    # Get database URLs
    sqlite_url = 'sqlite:///edutrack.db'
    postgres_url = os.getenv('DATABASE_URL')
    
    if not postgres_url:
        print("❌ DATABASE_URL not found in environment variables")
        return None, None
    
    return sqlite_url, postgres_url

def get_table_names(sqlite_engine):
    """Get all table names from SQLite database"""
    with sqlite_engine.connect() as conn:
        result = conn.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name;
        """))
        return [row[0] for row in result.fetchall()]

def get_table_schema(sqlite_engine, table_name):
    """Get table schema from SQLite"""
    with sqlite_engine.connect() as conn:
        result = conn.execute(text(f"PRAGMA table_info({table_name})"))
        return result.fetchall()

def migrate_table_data(sqlite_engine, postgres_engine, table_name):
    """Migrate data from SQLite table to PostgreSQL"""
    try:
        # Get all data from SQLite table
        with sqlite_engine.connect() as sqlite_conn:
            result = sqlite_conn.execute(text(f"SELECT * FROM {table_name}"))
            rows = result.fetchall()
            
            if not rows:
                print(f"  📝 Table {table_name} is empty, skipping...")
                return True
            
            print(f"  📊 Found {len(rows)} rows in {table_name}")
            
            # Get column names
            columns = list(rows[0].keys()) if rows else []
            
            # Insert data into PostgreSQL
            with postgres_engine.connect() as postgres_conn:
                # Clear existing data (optional - comment out if you want to keep existing data)
                postgres_conn.execute(text(f"DELETE FROM {table_name}"))
                postgres_conn.commit()
                
                # Insert new data
                for row in rows:
                    values = [getattr(row, col) for col in columns]
                    placeholders = ', '.join([':' + col for col in columns])
                    columns_str = ', '.join(columns)
                    
                    query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                    postgres_conn.execute(text(query), dict(zip(columns, values)))
                
                postgres_conn.commit()
                print(f"  ✅ Successfully migrated {len(rows)} rows to {table_name}")
                return True
                
    except Exception as e:
        print(f"  ❌ Error migrating {table_name}: {e}")
        return False

def main():
    """Main migration function"""
    print("🚀 Starting Migration from SQLite to Render PostgreSQL")
    print("=" * 60)
    
    # Load configuration
    sqlite_url, postgres_url = load_configuration()
    if not sqlite_url or not postgres_url:
        print("❌ Failed to load configuration")
        return False
    
    # Check if SQLite database exists
    if not os.path.exists('edutrack.db'):
        print("❌ SQLite database 'edutrack.db' not found")
        print("   Please ensure the database file exists in the current directory")
        return False
    
    try:
        # Create engines
        print("🔗 Connecting to databases...")
        sqlite_engine = create_engine(sqlite_url, echo=False)
        postgres_engine = create_engine(postgres_url, echo=False)
        
        # Test connections
        with sqlite_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ SQLite connection successful")
        
        with postgres_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ PostgreSQL connection successful")
        
        # Get table names
        print("\n📋 Discovering tables...")
        table_names = get_table_names(sqlite_engine)
        print(f"Found {len(table_names)} tables: {', '.join(table_names)}")
        
        # Migrate each table
        print("\n🔄 Starting data migration...")
        success_count = 0
        failed_tables = []
        
        for table_name in table_names:
            print(f"\n📦 Migrating table: {table_name}")
            if migrate_table_data(sqlite_engine, postgres_engine, table_name):
                success_count += 1
            else:
                failed_tables.append(table_name)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Migration Summary:")
        print(f"✅ Successfully migrated: {success_count}/{len(table_names)} tables")
        
        if failed_tables:
            print(f"❌ Failed tables: {', '.join(failed_tables)}")
        else:
            print("🎉 All tables migrated successfully!")
        
        print("\n💡 Next steps:")
        print("1. Test your Flask application with the new database")
        print("2. Verify all functionality works correctly")
        print("3. Consider backing up your SQLite database before removing it")
        
        return len(failed_tables) == 0
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
