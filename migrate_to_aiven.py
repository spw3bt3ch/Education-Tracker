#!/usr/bin/env python3
"""
Data Migration Script for Student Assignment Tracking App
Migrates data from SQLite to Aiven PostgreSQL/MySQL database
"""

import os
import sys
import json
import sqlite3
import psycopg
import pymysql
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

class DatabaseMigrator:
    def __init__(self):
        self.sqlite_db = 'instance/edutrack.db'
        self.postgres_url = os.getenv('DATABASE_URL')
        self.mysql_url = os.getenv('MYSQL_URL')
        
        # Tables to migrate in order (respecting foreign key constraints)
        self.tables = [
            'user',
            'class',
            'subject', 
            'student',
            'assignment',
            'assignment_record',
            'comment',
            'homework_record',
            'homework_comment',
            'message',
            'notification',
            'lesson',
            'lesson_plan',
            'lesson_note',
            'lesson_submission',
            'lesson_plan_submission',
            'lesson_note_submission',
            'setting'
        ]
        
        self.exported_data = {}
        
    def connect_sqlite(self):
        """Connect to SQLite database"""
        if not os.path.exists(self.sqlite_db):
            raise FileNotFoundError(f"SQLite database not found at {self.sqlite_db}")
        return sqlite3.connect(self.sqlite_db)
    
    def connect_postgres(self):
        """Connect to PostgreSQL database"""
        if not self.postgres_url:
            raise ValueError("PostgreSQL URL not provided in environment variables")
        
        parsed_url = urlparse(self.postgres_url)
        return psycopg.connect(
            host=parsed_url.hostname,
            port=parsed_url.port,
            dbname=parsed_url.path[1:],  # Remove leading slash
            user=parsed_url.username,
            password=parsed_url.password,
            sslmode='require'
        )
    
    def connect_mysql(self):
        """Connect to MySQL database"""
        if not self.mysql_url:
            raise ValueError("MySQL URL not provided in environment variables")
        
        parsed_url = urlparse(self.mysql_url)
        return pymysql.connect(
            host=parsed_url.hostname,
            port=parsed_url.port or 3306,
            database=parsed_url.path[1:],  # Remove leading slash
            user=parsed_url.username,
            password=parsed_url.password,
            ssl_disabled=False
        )
    
    def export_sqlite_data(self):
        """Export all data from SQLite database"""
        print("🔄 Exporting data from SQLite database...")
        
        conn = self.connect_sqlite()
        cursor = conn.cursor()
        
        for table in self.tables:
            try:
                # Get table schema
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in cursor.fetchall()]
                
                # Get all data from table
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                
                # Convert rows to list of dictionaries
                data = []
                for row in rows:
                    row_dict = {}
                    for i, value in enumerate(row):
                        # Handle datetime objects
                        if isinstance(value, str) and ('T' in value or ' ' in value):
                            try:
                                # Try to parse as datetime
                                datetime.fromisoformat(value.replace('Z', '+00:00'))
                            except:
                                pass
                        row_dict[columns[i]] = value
                    data.append(row_dict)
                
                self.exported_data[table] = {
                    'columns': columns,
                    'data': data,
                    'count': len(data)
                }
                
                print(f"  ✅ Exported {len(data)} records from {table}")
                
            except sqlite3.OperationalError as e:
                if "no such table" in str(e):
                    print(f"  ⚠️  Table {table} does not exist, skipping...")
                else:
                    print(f"  ❌ Error exporting {table}: {e}")
            except Exception as e:
                print(f"  ❌ Error exporting {table}: {e}")
        
        conn.close()
        print(f"✅ Export completed. Total tables exported: {len(self.exported_data)}")
    
    def save_export_data(self, filename='migration_data.json'):
        """Save exported data to JSON file"""
        print(f"💾 Saving exported data to {filename}...")
        
        # Convert datetime objects to strings for JSON serialization
        def json_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.exported_data, f, indent=2, default=json_serializer, ensure_ascii=False)
        
        print(f"✅ Data saved to {filename}")
    
    def load_export_data(self, filename='migration_data.json'):
        """Load exported data from JSON file"""
        print(f"📂 Loading data from {filename}...")
        
        with open(filename, 'r', encoding='utf-8') as f:
            self.exported_data = json.load(f)
        
        print(f"✅ Data loaded from {filename}")
    
    def import_to_postgres(self):
        """Import data to PostgreSQL database"""
        print("🔄 Importing data to PostgreSQL...")
        
        conn = self.connect_postgres()
        cursor = conn.cursor()
        
        try:
            for table in self.tables:
                if table not in self.exported_data:
                    continue
                
                table_data = self.exported_data[table]
                if not table_data['data']:
                    print(f"  ⚠️  No data to import for {table}")
                    continue
                
                # Prepare INSERT statement
                columns = table_data['columns']
                placeholders = ', '.join(['%s'] * len(columns))
                # Quote table name to handle reserved keywords like 'user'
                quoted_table = f'"{table}"'
                insert_sql = f"INSERT INTO {quoted_table} ({', '.join(columns)}) VALUES ({placeholders})"
                
                # Insert data
                for row in table_data['data']:
                    values = []
                    for col in columns:
                        value = row.get(col)
                        # Convert SQLite boolean (0/1) to PostgreSQL boolean
                        if col in ['is_active', 'completed', 'is_read'] and value is not None:
                            value = bool(value)
                        values.append(value)
                    cursor.execute(insert_sql, values)
                
                conn.commit()
                print(f"  ✅ Imported {len(table_data['data'])} records to {table}")
                
        except Exception as e:
            print(f"  ❌ Error importing to PostgreSQL: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def import_to_mysql(self):
        """Import data to MySQL database"""
        print("🔄 Importing data to MySQL...")
        
        conn = self.connect_mysql()
        cursor = conn.cursor()
        
        try:
            for table in self.tables:
                if table not in self.exported_data:
                    continue
                
                table_data = self.exported_data[table]
                if not table_data['data']:
                    print(f"  ⚠️  No data to import for {table}")
                    continue
                
                # Prepare INSERT statement
                columns = table_data['columns']
                placeholders = ', '.join(['%s'] * len(columns))
                insert_sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
                
                # Insert data
                for row in table_data['data']:
                    values = [row.get(col) for col in columns]
                    cursor.execute(insert_sql, values)
                
                conn.commit()
                print(f"  ✅ Imported {len(table_data['data'])} records to {table}")
                
        except Exception as e:
            print(f"  ❌ Error importing to MySQL: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def verify_migration(self, db_type='postgres'):
        """Verify that data was migrated correctly"""
        print(f"🔍 Verifying migration to {db_type}...")
        
        if db_type == 'postgres':
            conn = self.connect_postgres()
        else:
            conn = self.connect_mysql()
        
        cursor = conn.cursor()
        
        try:
            for table in self.tables:
                if table not in self.exported_data:
                    continue
                
                expected_count = self.exported_data[table]['count']
                # Quote table name to handle reserved keywords like 'user'
                quoted_table = f'"{table}"'
                cursor.execute(f"SELECT COUNT(*) FROM {quoted_table}")
                actual_count = cursor.fetchone()[0]
                
                if expected_count == actual_count:
                    print(f"  ✅ {table}: {actual_count} records (matches expected)")
                else:
                    print(f"  ❌ {table}: {actual_count} records (expected {expected_count})")
                    
        except Exception as e:
            print(f"  ❌ Error verifying {table}: {e}")
        finally:
            conn.close()
    
    def run_migration(self, target_db='postgres', export_file='migration_data.json'):
        """Run the complete migration process"""
        print("🚀 Starting database migration...")
        print(f"   Source: SQLite ({self.sqlite_db})")
        print(f"   Target: {target_db.upper()}")
        print(f"   Export file: {export_file}")
        print("-" * 50)
        
        try:
            # Step 1: Export from SQLite
            self.export_sqlite_data()
            
            # Step 2: Save export data
            self.save_export_data(export_file)
            
            # Step 3: Import to target database
            if target_db == 'postgres':
                self.import_to_postgres()
            elif target_db == 'mysql':
                self.import_to_mysql()
            else:
                raise ValueError(f"Unsupported target database: {target_db}")
            
            # Step 4: Verify migration
            self.verify_migration(target_db)
            
            print("-" * 50)
            print("✅ Migration completed successfully!")
            print(f"📁 Backup data saved to: {export_file}")
            print("🔧 Update your .env file with the new DATABASE_URL")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            sys.exit(1)

def main():
    """Main function to run migration"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate Student Assignment Tracking App database to Aiven')
    parser.add_argument('--target', choices=['postgres', 'mysql'], default='postgres',
                       help='Target database type (default: postgres)')
    parser.add_argument('--export-only', action='store_true',
                       help='Only export data from SQLite, do not import')
    parser.add_argument('--import-only', action='store_true',
                       help='Only import from existing export file')
    parser.add_argument('--export-file', default='migration_data.json',
                       help='Export file name (default: migration_data.json)')
    
    args = parser.parse_args()
    
    migrator = DatabaseMigrator()
    
    if args.export_only:
        migrator.export_sqlite_data()
        migrator.save_export_data(args.export_file)
    elif args.import_only:
        migrator.load_export_data(args.export_file)
        if args.target == 'postgres':
            migrator.import_to_postgres()
        else:
            migrator.import_to_mysql()
        migrator.verify_migration(args.target)
    else:
        migrator.run_migration(args.target, args.export_file)

if __name__ == '__main__':
    main()
