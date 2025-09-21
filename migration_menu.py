#!/usr/bin/env python3
"""
Migration Menu for Student Assignment Tracking App
Interactive menu for Aiven database migration
"""

import os
import sys
import subprocess

def print_banner():
    """Print application banner"""
    print("=" * 70)
    print("🎓 Student Assignment Tracking App - Aiven Migration")
    print("=" * 70)
    print("Choose an option to get started:")
    print()

def show_menu():
    """Show the main menu"""
    print("📋 Migration Options:")
    print()
    print("1. 🚀 Quick Migration (Recommended)")
    print("   - Automated migration with guided setup")
    print("   - Handles everything automatically")
    print()
    print("2. 📤 Export Data Only")
    print("   - Export SQLite data to JSON file")
    print("   - Useful for manual migration")
    print()
    print("3. 🏗️  Setup Aiven Database")
    print("   - Create tables in Aiven database")
    print("   - Test database connection")
    print()
    print("4. 📥 Import Data Only")
    print("   - Import from existing export file")
    print("   - Requires previous export")
    print()
    print("5. 💾 Backup SQLite Database")
    print("   - Create backup before migration")
    print("   - Safety first!")
    print()
    print("6. 🧪 Test Database Connection")
    print("   - Verify Aiven database connectivity")
    print("   - Check configuration")
    print()
    print("7. 🚀 Production Deployment Setup")
    print("   - Configure for production")
    print("   - Create deployment files")
    print()
    print("8. 📚 View Migration Guide")
    print("   - Open detailed documentation")
    print()
    print("9. ❌ Exit")
    print()

def run_quick_migration():
    """Run quick migration"""
    print("🚀 Starting Quick Migration...")
    try:
        subprocess.run([sys.executable, 'quick_migrate.py'])
    except KeyboardInterrupt:
        print("\n❌ Migration cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")

def run_export():
    """Run data export"""
    print("📤 Exporting data from SQLite...")
    try:
        subprocess.run([sys.executable, 'migrate_to_aiven.py', '--export-only'])
    except KeyboardInterrupt:
        print("\n❌ Export cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")

def run_setup():
    """Run database setup"""
    print("🏗️  Setting up Aiven database...")
    try:
        subprocess.run([sys.executable, 'setup_aiven.py'])
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")

def run_import():
    """Run data import"""
    print("📥 Importing data to Aiven...")
    print("Choose database type:")
    print("1. PostgreSQL")
    print("2. MySQL")
    
    choice = input("Enter choice (1 or 2): ").strip()
    if choice == '1':
        db_type = 'postgres'
    elif choice == '2':
        db_type = 'mysql'
    else:
        print("❌ Invalid choice")
        return
    
    try:
        subprocess.run([sys.executable, 'migrate_to_aiven.py', '--import-only', '--target', db_type])
    except KeyboardInterrupt:
        print("\n❌ Import cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")

def run_backup():
    """Run database backup"""
    print("💾 Creating SQLite backup...")
    try:
        subprocess.run([sys.executable, 'backup_sqlite.py'])
    except KeyboardInterrupt:
        print("\n❌ Backup cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")

def run_test():
    """Run connection test"""
    print("🧪 Testing database connection...")
    try:
        subprocess.run([sys.executable, 'setup_aiven.py', '--test-only'])
    except KeyboardInterrupt:
        print("\n❌ Test cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")

def run_deployment():
    """Run deployment setup"""
    print("🚀 Setting up production deployment...")
    try:
        subprocess.run([sys.executable, 'deploy_aiven.py'])
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")

def show_guide():
    """Show migration guide"""
    print("📚 Migration Guide")
    print("=" * 50)
    print()
    print("📖 Detailed documentation is available in:")
    print("   • AIVEN_MIGRATION_GUIDE.md")
    print()
    print("🔧 Configuration files:")
    print("   • config.env.example - Environment template")
    print("   • .env - Your actual configuration (create this)")
    print()
    print("📜 Migration scripts:")
    print("   • migrate_to_aiven.py - Main migration script")
    print("   • setup_aiven.py - Database setup script")
    print("   • quick_migrate.py - Automated migration")
    print("   • backup_sqlite.py - Backup utility")
    print("   • deploy_aiven.py - Production setup")
    print()
    print("🚀 Quick start:")
    print("   1. Copy config.env.example to .env")
    print("   2. Update .env with your Aiven database details")
    print("   3. Run: python quick_migrate.py")
    print()
    input("Press Enter to continue...")

def main():
    """Main menu loop"""
    while True:
        print_banner()
        show_menu()
        
        try:
            choice = input("Enter your choice (1-9): ").strip()
            print()
            
            if choice == '1':
                run_quick_migration()
            elif choice == '2':
                run_export()
            elif choice == '3':
                run_setup()
            elif choice == '4':
                run_import()
            elif choice == '5':
                run_backup()
            elif choice == '6':
                run_test()
            elif choice == '7':
                run_deployment()
            elif choice == '8':
                show_guide()
            elif choice == '9':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-9.")
            
            print("\n" + "="*50)
            input("Press Enter to continue...")
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            input("Press Enter to continue...")

if __name__ == '__main__':
    main()
