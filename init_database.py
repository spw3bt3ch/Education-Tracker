#!/usr/bin/env python3
"""
Database initialization script for Render deployment
This script creates the database tables and demo data
"""

from app import app, db, User, School, SchoolSubscription, SubscriptionPlan
from payment_service import PaymentService
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def init_database():
    """Initialize database with tables and demo data"""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Create subscription plans
            payment_service = PaymentService()
            payment_service.create_default_plans()
            print("✅ Subscription plans created")
            
            # Create demo accounts if they don't exist
            create_demo_accounts()
            
            print("✅ Database initialization completed successfully")
            
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            raise

def create_demo_accounts():
    """Create demo accounts for testing"""
    with app.app_context():
        # Create Super Admin if it doesn't exist
        if not User.query.filter_by(username='superadmin').first():
            superadmin = User(
                username='superadmin',
                email='superadmin@edutrack.com',
                password_hash=generate_password_hash('superadmin123'),
                role='super_admin',
                first_name='Super',
                last_name='Admin',
                is_active=True
            )
            db.session.add(superadmin)
            print("✅ Super admin created")

        # Create Demo School if it doesn't exist
        demo_school = School.query.filter_by(code='DEMO001').first()
        if not demo_school:
            demo_school = School(
                name='Demo Academy',
                code='DEMO001',
                address='123 Education Street, Lagos',
                phone='+234-123-456-7890',
                email='info@demoacademy.com',
                website='www.demoacademy.com',
                is_active=True
            )
            db.session.add(demo_school)
            db.session.flush()  # Get the school ID
            print("✅ Demo school created")

        # Create other demo accounts
        demo_accounts = [
            {
                'username': 'admin',
                'email': 'admin@demoacademy.com',
                'password': 'admin123',
                'role': 'admin',
                'first_name': 'John',
                'last_name': 'Doe'
            },
            {
                'username': 'teacher1',
                'email': 'teacher1@demoacademy.com',
                'password': 'teacher123',
                'role': 'teacher',
                'first_name': 'Sarah',
                'last_name': 'Johnson'
            },
            {
                'username': 'parent1',
                'email': 'parent1@demoacademy.com',
                'password': 'parent123',
                'role': 'parent',
                'first_name': 'Michael',
                'last_name': 'Brown'
            },
            {
                'username': 'student1',
                'email': 'student1@demoacademy.com',
                'password': 'student123',
                'role': 'student',
                'first_name': 'Emma',
                'last_name': 'Wilson'
            }
        ]

        for account_data in demo_accounts:
            if not User.query.filter_by(username=account_data['username']).first():
                user = User(
                    username=account_data['username'],
                    email=account_data['email'],
                    password_hash=generate_password_hash(account_data['password']),
                    role=account_data['role'],
                    first_name=account_data['first_name'],
                    last_name=account_data['last_name'],
                    school_id=demo_school.id,
                    is_active=True
                )
                db.session.add(user)
                print(f"✅ {account_data['role']} account created: {account_data['username']}")

        # Create subscription for demo school
        if not SchoolSubscription.query.filter_by(school_id=demo_school.id).first():
            free_trial_plan = SubscriptionPlan.query.filter_by(name='Free Trial').first()
            if free_trial_plan:
                subscription = SchoolSubscription(
                    school_id=demo_school.id,
                    plan_id=free_trial_plan.id,
                    status='active',
                    start_date=datetime.utcnow(),
                    end_date=datetime.utcnow() + timedelta(days=7)
                )
                db.session.add(subscription)
                print("✅ Free trial subscription created")

        db.session.commit()

if __name__ == '__main__':
    init_database()
