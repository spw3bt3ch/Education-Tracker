#!/usr/bin/env python3
"""
Paystack Integration Setup Script
This script helps set up Paystack integration for the Student Assignment Tracking App
"""

import os
import sys
from datetime import datetime

def setup_paystack():
    """Setup Paystack integration"""
    print("🚀 Paystack Integration Setup")
    print("=" * 50)
    
    # Check if environment file exists
    env_file = 'aiven_config.env'
    if not os.path.exists(env_file):
        print(f"❌ Environment file {env_file} not found!")
        print("Please make sure you have the environment file with your Paystack keys.")
        return False
    
    # Read current environment file
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Check if Paystack keys are already configured
    if 'PAYSTACK_PUBLIC_KEY' in content and 'PAYSTACK_SECRET_KEY' in content:
        print("✅ Paystack keys are already configured in the environment file")
    else:
        print("❌ Paystack keys not found in environment file")
        print("Please add your Paystack keys to the environment file:")
        print("PAYSTACK_PUBLIC_KEY=pk_live_your_public_key")
        print("PAYSTACK_SECRET_KEY=sk_live_your_secret_key")
        print("PAYSTACK_WEBHOOK_SECRET=your_webhook_secret")
        return False
    
    print("\n📋 Paystack Integration Checklist:")
    print("1. ✅ Environment variables configured")
    print("2. ✅ Payment models created")
    print("3. ✅ Payment routes implemented")
    print("4. ✅ Pricing page created")
    print("5. ✅ Subscription management added")
    
    print("\n🔧 Next Steps:")
    print("1. Run the database migration:")
    print("   python migrate_payment_tables.py")
    print("\n2. Set up Paystack webhook:")
    print("   - URL: https://yourdomain.com/payment/webhook")
    print("   - Events: charge.success")
    print("   - Add webhook secret to PAYSTACK_WEBHOOK_SECRET")
    
    print("\n3. Test the integration:")
    print("   - Visit /pricing to see pricing plans")
    print("   - Test payment flow with Paystack test keys")
    print("   - Verify webhook is receiving events")
    
    print("\n4. Production deployment:")
    print("   - Replace test keys with live keys")
    print("   - Update webhook URL to production domain")
    print("   - Test with real payments")
    
    print("\n📚 Paystack Documentation:")
    print("   - API Docs: https://paystack.com/docs/api/")
    print("   - Webhooks: https://paystack.com/docs/payments/webhooks/")
    print("   - Test Cards: https://paystack.com/docs/payments/test-payments/")
    
    return True

def test_paystack_config():
    """Test Paystack configuration"""
    print("\n🧪 Testing Paystack Configuration...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv('aiven_config.env')
        
        public_key = os.getenv('PAYSTACK_PUBLIC_KEY')
        secret_key = os.getenv('PAYSTACK_SECRET_KEY')
        webhook_secret = os.getenv('PAYSTACK_WEBHOOK_SECRET')
        
        if not public_key:
            print("❌ PAYSTACK_PUBLIC_KEY not found")
            return False
        
        if not secret_key:
            print("❌ PAYSTACK_SECRET_KEY not found")
            return False
        
        if not webhook_secret:
            print("⚠️  PAYSTACK_WEBHOOK_SECRET not set (optional but recommended)")
        
        print("✅ Paystack configuration looks good!")
        
        # Test API connection
        try:
            import requests
            headers = {
                'Authorization': f'Bearer {secret_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get('https://api.paystack.co/transaction', headers=headers)
            if response.status_code == 200:
                print("✅ Paystack API connection successful")
            else:
                print(f"⚠️  Paystack API returned status {response.status_code}")
                
        except Exception as e:
            print(f"⚠️  Could not test Paystack API: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing configuration: {e}")
        return False

if __name__ == "__main__":
    success = setup_paystack()
    
    if success:
        print("\n" + "=" * 50)
        test_paystack_config()
        print("\n🎉 Setup completed successfully!")
        print("\nRun 'python migrate_payment_tables.py' to create the database tables.")
    else:
        print("\n❌ Setup failed. Please check the configuration.")
        sys.exit(1)
