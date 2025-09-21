#!/usr/bin/env python3
"""
SQLite Backup Script for Student Assignment Tracking App
Creates a backup of your SQLite database before migration
"""

import os
import shutil
import sqlite3
import json
from datetime import datetime

def create_backup():
    """Create a backup of the SQLite database"""
    print("🔄 Creating SQLite database backup...")
    
    # Check if database exists
    db_path = 'instance/edutrack.db'
    if not os.path.exists(db_path):
        print("❌ SQLite database not found at instance/edutrack.db")
        return False
    
    # Create backup directory
    backup_dir = 'backups'
    os.makedirs(backup_dir, exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"edutrack_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    try:
        # Copy database file
        shutil.copy2(db_path, backup_path)
        print(f"✅ Database backed up to: {backup_path}")
        
        # Create metadata file
        metadata = {
            'backup_date': datetime.now().isoformat(),
            'original_path': db_path,
            'backup_path': backup_path,
            'file_size': os.path.getsize(backup_path),
            'tables': get_table_info(db_path)
        }
        
        metadata_path = os.path.join(backup_dir, f"backup_metadata_{timestamp}.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Backup metadata saved to: {metadata_path}")
        
        # Create a symbolic link to latest backup
        latest_backup = os.path.join(backup_dir, 'latest_backup.db')
        if os.path.exists(latest_backup):
            os.remove(latest_backup)
        os.symlink(backup_filename, latest_backup)
        
        print(f"✅ Latest backup link created: {latest_backup}")
        
        return True
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False

def get_table_info(db_path):
    """Get information about tables in the database"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Get row counts for each table
        table_info = {}
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            table_info[table] = count
        
        conn.close()
        return table_info
        
    except Exception as e:
        print(f"⚠️  Could not get table info: {e}")
        return {}

def list_backups():
    """List all available backups"""
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        print("No backups found")
        return
    
    print("📁 Available backups:")
    for filename in sorted(os.listdir(backup_dir)):
        if filename.endswith('.db'):
            filepath = os.path.join(backup_dir, filename)
            size = os.path.getsize(filepath)
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            print(f"  • {filename} ({size:,} bytes, {mtime.strftime('%Y-%m-%d %H:%M:%S')})")

def restore_backup(backup_filename):
    """Restore from a backup"""
    backup_path = os.path.join('backups', backup_filename)
    
    if not os.path.exists(backup_path):
        print(f"❌ Backup file not found: {backup_path}")
        return False
    
    # Create instance directory if it doesn't exist
    os.makedirs('instance', exist_ok=True)
    
    try:
        # Copy backup to current database location
        shutil.copy2(backup_path, 'instance/edutrack.db')
        print(f"✅ Database restored from: {backup_filename}")
        return True
        
    except Exception as e:
        print(f"❌ Restore failed: {e}")
        return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Backup and restore SQLite database')
    parser.add_argument('--list', action='store_true', help='List available backups')
    parser.add_argument('--restore', help='Restore from backup (specify backup filename)')
    
    args = parser.parse_args()
    
    if args.list:
        list_backups()
    elif args.restore:
        restore_backup(args.restore)
    else:
        create_backup()

if __name__ == '__main__':
    main()
