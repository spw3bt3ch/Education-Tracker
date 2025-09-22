#!/usr/bin/env python3
"""
Migration script to add payment and subscription tables
Run this script to add the new payment-related tables to your database
"""

import os
import sys
from datetime import datetime
import json

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, SubscriptionPlan, SchoolSubscription, Payment

def migrate_payment_tables():
    """Create payment and subscription tables"""
    with app.app_context():
        try:
            print("🔄 Starting payment tables migration...")
            
            # Create all tables
            db.create_all()
            print("✅ Payment tables created successfully")
            
            # Create default subscription plans
            print("🔄 Creating default subscription plans...")
            
            plans_data = [
                {
                    'name': 'Free Trial',
                    'price': 0.0,
                    'duration_days': 7,
                    'features': json.dumps([
                        '1 week access',
                        'Up to 50 students',
                        'Basic features',
                        'Email support'
                    ])
                },
                {
                    'name': 'Monthly Plan',
                    'price': 10000.0,
                    'duration_days': 30,
                    'features': json.dumps([
                        'Unlimited students',
                        'All features included',
                        'Priority support',
                        'Data backup'
                    ])
                },
                {
                    'name': 'Annual Plan',
                    'price': 100000.0,
                    'duration_days': 365,
                    'features': json.dumps([
                        'Unlimited students',
                        'All features included',
                        'Priority support',
                        'Advanced analytics',
                        'Custom integrations'
                    ])
                },
                {
                    'name': 'Lifetime Plan',
                    'price': 500000.0,
                    'duration_days': None,  # Lifetime
                    'features': json.dumps([
                        'Unlimited students',
                        'All features included',
                        '24/7 premium support',
                        'Custom development',
                        'White-label options',
                        'Lifetime updates'
                    ])
                }
            ]
            
            for plan_data in plans_data:
                existing_plan = SubscriptionPlan.query.filter_by(name=plan_data['name']).first()
                if not existing_plan:
                    plan = SubscriptionPlan(**plan_data)
                    db.session.add(plan)
                    print(f"✅ Created plan: {plan_data['name']}")
                else:
                    print(f"⚠️  Plan already exists: {plan_data['name']}")
            
            db.session.commit()
            print("✅ Default subscription plans created successfully")
            
            print("\n🎉 Payment tables migration completed successfully!")
            print("\nNext steps:")
            print("1. Set up your Paystack webhook URL: https://yourdomain.com/payment/webhook")
            print("2. Configure webhook events: charge.success")
            print("3. Test payment flow with your Paystack test keys")
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            db.session.rollback()
            return False
        
        return True

if __name__ == "__main__":
    print("🚀 Payment Tables Migration Script")
    print("=" * 50)
    
    success = migrate_payment_tables()
    
    if success:
        print("\n✅ Migration completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)
