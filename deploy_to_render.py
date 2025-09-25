#!/usr/bin/env python3
"""
Deployment helper script for SMIED to Render.com
This script helps prepare and deploy the application
"""

import os
import subprocess
import sys

def print_banner():
    """Print deployment banner"""
    print("=" * 70)
    print("🚀 SMIED - Render.com Deployment Helper")
    print("=" * 70)
    print("This script will help you deploy SMIED to Render.com")
    print()

def check_git_status():
    """Check git status and ensure everything is committed"""
    print("🔍 Checking git status...")
    
    try:
        # Check if we're in a git repository
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ Not in a git repository. Please run 'git init' first.")
            return False
        
        # Check for uncommitted changes
        if result.stdout.strip():
            print("⚠️  Uncommitted changes detected:")
            print(result.stdout)
            
            commit = input("Do you want to commit these changes? (y/N): ")
            if commit.lower() == 'y':
                message = input("Enter commit message: ")
                if not message:
                    message = "Deploy to Render.com"
                
                subprocess.run(['git', 'add', '.'])
                subprocess.run(['git', 'commit', '-m', message])
                print("✅ Changes committed")
            else:
                print("❌ Please commit changes before deploying")
                return False
        else:
            print("✅ All changes committed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking git status: {e}")
        return False

def check_requirements():
    """Check if requirements.txt exists and is complete"""
    print("\n📦 Checking requirements...")
    
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found")
        return False
    
    # Read requirements.txt
    with open('requirements.txt', 'r') as f:
        requirements = f.read()
    
    # Check for essential packages
    essential_packages = [
        'Flask',
        'Flask-SQLAlchemy',
        'Flask-Login',
        'Werkzeug',
        'python-dotenv',
        'psycopg2-binary',
        'Flask-Mail'
    ]
    
    missing_packages = []
    for package in essential_packages:
        if package.lower() not in requirements.lower():
            missing_packages.append(package)
    
    if missing_packages:
        print(f"⚠️  Missing packages in requirements.txt: {', '.join(missing_packages)}")
        print("   Consider adding them before deploying")
    else:
        print("✅ Essential packages found in requirements.txt")
    
    return True

def check_environment_files():
    """Check for environment configuration files"""
    print("\n🔧 Checking environment configuration...")
    
    env_files = ['.env', 'aiven_config.env', 'env.template']
    found_files = []
    
    for file in env_files:
        if os.path.exists(file):
            found_files.append(file)
    
    if found_files:
        print(f"✅ Found environment files: {', '.join(found_files)}")
        print("   Remember to set up environment variables in Render dashboard")
    else:
        print("⚠️  No environment files found")
        print("   You'll need to set up environment variables manually in Render")
    
    return True

def show_deployment_steps():
    """Show step-by-step deployment instructions"""
    print("\n" + "="*70)
    print("📋 DEPLOYMENT STEPS")
    print("="*70)
    print()
    print("1. 🌐 Push to GitHub:")
    print("   git remote add origin https://github.com/YOUR_USERNAME/smied.git")
    print("   git branch -M main")
    print("   git push -u origin main")
    print()
    print("2. 🚀 Deploy to Render:")
    print("   - Go to https://render.com")
    print("   - Sign in with GitHub")
    print("   - Click 'New +' → 'Web Service'")
    print("   - Connect your repository")
    print("   - Set build command: pip install -r requirements.txt")
    print("   - Set start command: python app.py")
    print()
    print("3. 🔧 Configure Environment Variables in Render:")
    print("   - DATABASE_URL (your production database)")
    print("   - SECRET_KEY (strong random string)")
    print("   - MAIL_SERVER, MAIL_USERNAME, MAIL_PASSWORD")
    print("   - PAYSTACK_PUBLIC_KEY, PAYSTACK_SECRET_KEY")
    print()
    print("4. ✅ Deploy and Test:")
    print("   - Click 'Deploy' in Render")
    print("   - Wait for deployment to complete")
    print("   - Test your application")
    print()
    print("🔗 Your app will be available at:")
    print("   https://your-app-name.onrender.com")

def main():
    """Main deployment function"""
    print_banner()
    
    try:
        # Check git status
        if not check_git_status():
            print("💥 Deployment preparation failed")
            return False
        
        # Check requirements
        if not check_requirements():
            print("💥 Requirements check failed")
            return False
        
        # Check environment files
        if not check_environment_files():
            print("💥 Environment check failed")
            return False
        
        # Show deployment steps
        show_deployment_steps()
        
        print("\n" + "="*70)
        print("🎉 Ready for deployment!")
        print("="*70)
        print()
        print("✅ All checks passed")
        print("✅ Code is committed")
        print("✅ Ready to push to GitHub and deploy to Render")
        print()
        print("📚 For detailed instructions, see DEPLOYMENT.md")
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Deployment preparation cancelled")
        return False
    except Exception as e:
        print(f"\n💥 Error: {e}")
        return False

if __name__ == '__main__':
    main()

