"""
Payment Service for Student Assignment Tracking App
Handles Paystack integration for subscription payments
"""

import requests
import json
import hashlib
import hmac
from datetime import datetime, timedelta
from flask import current_app

class PaymentService:
    """Service class for handling payment operations"""
    
    def __init__(self):
        self.base_url = "https://api.paystack.co"
    
    def _get_config(self):
        """Get Paystack configuration from current app context"""
        return {
            'public_key': current_app.config.get('PAYSTACK_PUBLIC_KEY'),
            'secret_key': current_app.config.get('PAYSTACK_SECRET_KEY'),
            'webhook_secret': current_app.config.get('PAYSTACK_WEBHOOK_SECRET')
        }
    
    def _get_db_models(self):
        """Get database models within proper Flask context"""
        # Import models within the current Flask app context
        from app import db, SubscriptionPlan, School, Payment, SchoolSubscription, User
        return db, SubscriptionPlan, School, Payment, SchoolSubscription, User
    
    def initialize_payment(self, school_id, plan_id, email, amount, reference=None, admin_username=None, admin_password=None):
        """
        Initialize a payment with Paystack
        Returns payment authorization URL
        """
        try:
            # Get database models within proper Flask context
            db, SubscriptionPlan, School, Payment, SchoolSubscription, User = self._get_db_models()
            
            # Get plan details
            plan = SubscriptionPlan.query.get(plan_id)
            if not plan:
                return None, "Invalid plan selected"
            
            # Get school details
            school = School.query.get(school_id)
            if not school:
                return None, "School not found"
            
            # Generate reference if not provided
            if not reference:
                reference = f"EDU_{school_id}_{plan_id}_{int(datetime.now().timestamp())}"
            
            # Create payment record
            payment = Payment(
                school_id=school_id,
                plan_id=plan_id,
                amount=amount,
                paystack_reference=reference,
                status='pending'
            )
            db.session.add(payment)
            db.session.commit()
            
            # Store admin credentials for later use in welcome email
            self.admin_username = admin_username
            self.admin_password = admin_password
            
            # Get configuration
            config = self._get_config()
            
            # Prepare Paystack request
            headers = {
                'Authorization': f'Bearer {config["secret_key"]}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'email': email,
                'amount': int(amount * 100),  # Convert to kobo
                'reference': reference,
                'callback_url': f"{current_app.config['BASE_URL']}/payment/callback",
                'metadata': {
                    'school_id': school_id,
                    'plan_id': plan_id,
                    'school_name': school.name
                }
            }
            
            # Make request to Paystack
            response = requests.post(
                f"{self.base_url}/transaction/initialize",
                headers=headers,
                data=json.dumps(data)
            )
            
            if response.status_code == 200:
                result = response.json()
                if result['status']:
                    return result['data']['authorization_url'], None
                else:
                    return None, result['message']
            else:
                return None, f"Payment initialization failed: {response.status_code} - {response.text}"
                
        except Exception as e:
            return None, f"Error initializing payment: {str(e)}"
    
    def verify_payment(self, reference):
        """
        Verify payment status with Paystack
        Returns payment details if successful
        """
        try:
            config = self._get_config()
            headers = {
                'Authorization': f'Bearer {config["secret_key"]}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.base_url}/transaction/verify/{reference}",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if result['status'] and result['data']['status'] == 'success':
                    return result['data'], None
                else:
                    return None, "Payment verification failed"
            else:
                return None, f"Verification request failed: {response.status_code}"
                
        except Exception as e:
            return None, f"Error verifying payment: {str(e)}"
    
    def process_successful_payment(self, payment_data):
        """
        Process a successful payment and activate subscription
        """
        try:
            # Get database models within proper Flask context
            db, SubscriptionPlan, School, Payment, SchoolSubscription, User = self._get_db_models()
            
            reference = payment_data['reference']
            
            # Get payment record
            payment = Payment.query.filter_by(paystack_reference=reference).first()
            if not payment:
                return False, "Payment record not found"
            
            # Update payment status
            payment.status = 'success'
            payment.paystack_transaction_id = payment_data['id']
            payment.payment_method = payment_data.get('channel', 'unknown')
            payment.updated_at = datetime.utcnow()
            
            # Get plan details
            plan = SubscriptionPlan.query.get(payment.plan_id)
            
            # Calculate subscription end date
            end_date = None
            if plan.duration_days:
                end_date = datetime.utcnow() + timedelta(days=plan.duration_days)
            
            # Create or update school subscription
            existing_subscription = SchoolSubscription.query.filter_by(
                school_id=payment.school_id
            ).first()
            
            is_new_subscription = False
            if existing_subscription:
                # Update existing subscription
                existing_subscription.plan_id = payment.plan_id
                existing_subscription.status = 'active'
                existing_subscription.start_date = datetime.utcnow()
                existing_subscription.end_date = end_date
                existing_subscription.updated_at = datetime.utcnow()
            else:
                # Create new subscription
                subscription = SchoolSubscription(
                    school_id=payment.school_id,
                    plan_id=payment.plan_id,
                    status='active',
                    start_date=datetime.utcnow(),
                    end_date=end_date
                )
                db.session.add(subscription)
                is_new_subscription = True
            
            db.session.commit()
            
            # Send welcome email for new subscriptions
            if is_new_subscription:
                admin_user = User.query.filter_by(
                    school_id=payment.school_id,
                    role='school_admin'
                ).first()
                if admin_user:
                    self.send_welcome_email(payment.school_id, admin_user, plan)
            
            return True, "Subscription activated successfully"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error processing payment: {str(e)}"
    
    def verify_webhook(self, payload, signature):
        """
        Verify Paystack webhook signature
        """
        config = self._get_config()
        if not config['webhook_secret']:
            return False
        
        try:
            expected_signature = hmac.new(
                config['webhook_secret'].encode('utf-8'),
                payload,
                hashlib.sha512
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        except Exception:
            return False
    
    def get_school_subscription(self, school_id):
        """
        Get current school subscription details
        """
        # Get database models within proper Flask context
        db, SubscriptionPlan, School, Payment, SchoolSubscription, User = self._get_db_models()
        subscription = SchoolSubscription.query.filter_by(
            school_id=school_id,
            status='active'
        ).first()
        
        if not subscription:
            return None
        
        # Check if subscription has expired
        if subscription.end_date and subscription.end_date < datetime.utcnow():
            subscription.status = 'expired'
            db.session.commit()
            return None
        
        return subscription
    
    def is_subscription_active(self, school_id):
        """
        Check if school has an active subscription
        """
        # Get database models within proper Flask context
        db, SubscriptionPlan, School, Payment, SchoolSubscription, User = self._get_db_models()
        
        # Check if this is the demo school - demo school doesn't need subscription
        school = School.query.get(school_id)
        if school and school.name == 'Demo School':
            return True
        
        subscription = self.get_school_subscription(school_id)
        if not subscription:
            return False
        
        # Check if subscription has expired
        if subscription.end_date and subscription.end_date < datetime.utcnow():
            # Mark subscription as expired
            subscription.status = 'expired'
            db.session.commit()
            return False
        
        return subscription.status == 'active'
    
    def check_and_update_expired_subscriptions(self):
        """
        Check all subscriptions and mark expired ones as inactive
        This should be called periodically (e.g., via cron job)
        """
        try:
            # Get database models within proper Flask context
            db, SubscriptionPlan, School, Payment, SchoolSubscription, User = self._get_db_models()
            
            # Check for expiring subscriptions (7 days warning)
            expiring_subscriptions = SchoolSubscription.query.filter(
                SchoolSubscription.status == 'active',
                SchoolSubscription.end_date.isnot(None),
                SchoolSubscription.end_date > datetime.utcnow(),
                SchoolSubscription.end_date <= datetime.utcnow() + timedelta(days=7)
            ).all()
            
            # Send warning emails for expiring subscriptions
            for subscription in expiring_subscriptions:
                days_remaining = (subscription.end_date - datetime.utcnow()).days
                if days_remaining > 0:
                    self.send_expiration_warning_email(subscription.school_id, days_remaining)
            
            # Check for expired subscriptions
            expired_subscriptions = SchoolSubscription.query.filter(
                SchoolSubscription.status == 'active',
                SchoolSubscription.end_date.isnot(None),
                SchoolSubscription.end_date < datetime.utcnow()
            ).all()
            
            # Mark as expired and send notification emails
            for subscription in expired_subscriptions:
                subscription.status = 'expired'
                print(f"Subscription expired for school {subscription.school_id}")
                
                # Send expired notification email
                self.send_expired_notification_email(subscription.school_id)
            
            db.session.commit()
            return len(expired_subscriptions)
            
        except Exception as e:
            print(f"Error checking expired subscriptions: {e}")
            return 0
    
    def get_subscription_status_with_details(self, school_id):
        """
        Get detailed subscription status including expiration info
        """
        subscription = self.get_school_subscription(school_id)
        
        if not subscription:
            return {
                'is_active': False,
                'status': 'no_subscription',
                'message': 'No active subscription found',
                'days_remaining': 0,
                'expires_at': None
            }
        
        if subscription.status != 'active':
            return {
                'is_active': False,
                'status': subscription.status,
                'message': f'Subscription is {subscription.status}',
                'days_remaining': 0,
                'expires_at': subscription.end_date.isoformat() if subscription.end_date else None
            }
        
        # Calculate days remaining
        days_remaining = 0
        if subscription.end_date:
            days_remaining = (subscription.end_date - datetime.utcnow()).days
        
        return {
            'is_active': True,
            'status': 'active',
            'message': 'Subscription is active',
            'days_remaining': max(0, days_remaining),
            'expires_at': subscription.end_date.isoformat() if subscription.end_date else None,
            'plan_name': SubscriptionPlan.query.get(subscription.plan_id).name if subscription.plan_id else 'Unknown'
        }
    
    def get_plan_features(self, plan_id):
        """
        Get features for a specific plan
        """
        plan = SubscriptionPlan.query.get(plan_id)
        if plan and plan.features:
            try:
                return json.loads(plan.features)
            except:
                return []
        return []
    
    def send_welcome_email(self, school_id, admin_user, plan):
        """
        Send welcome email to new subscriber
        """
        try:
            from email_service import EmailService
            from datetime import datetime
            
            school = School.query.get(school_id)
            if not school or not admin_user:
                return False
            
            # Get plan features
            features = self.get_plan_features(plan.id)
            
            # Prepare email data
            email_data = {
                'admin_name': f"{admin_user.first_name} {admin_user.last_name}",
                'admin_email': admin_user.email,
                'school_name': school.name,
                'school_code': school.code,
                'plan_name': plan.name,
                'start_date': datetime.utcnow().strftime('%B %d, %Y'),
                'end_date': None,
                'features': features,
                'dashboard_url': f"{current_app.config['BASE_URL']}/admin/dashboard",
                'pricing_url': f"{current_app.config['BASE_URL']}/pricing"
            }
            
            # Set end date for time-based plans
            if plan.duration_days:
                end_date = datetime.utcnow() + timedelta(days=plan.duration_days)
                email_data['end_date'] = end_date.strftime('%B %d, %Y')
            
            # Send email
            EmailService.send_subscription_welcome_email(admin_user, school, plan, email_data, getattr(self, 'admin_username', admin_user.username), getattr(self, 'admin_password', None))
            return True
            
        except Exception as e:
            print(f"Error sending welcome email: {e}")
            return False
    
    def send_expiration_warning_email(self, school_id, days_remaining):
        """
        Send expiration warning email
        """
        try:
            from email_service import EmailService
            from datetime import datetime
            
            school = School.query.get(school_id)
            if not school:
                return False
            
            # Get admin user
            admin_user = User.query.filter_by(
                school_id=school_id,
                role='school_admin'
            ).first()
            
            if not admin_user:
                return False
            
            # Get subscription details
            subscription = self.get_school_subscription(school_id)
            if not subscription:
                return False
            
            plan = SubscriptionPlan.query.get(subscription.plan_id)
            if not plan:
                return False
            
            # Prepare email data
            email_data = {
                'admin_name': f"{admin_user.first_name} {admin_user.last_name}",
                'admin_email': admin_user.email,
                'school_name': school.name,
                'school_code': school.code,
                'plan_name': plan.name,
                'days_remaining': days_remaining,
                'expiry_date': subscription.end_date.strftime('%B %d, %Y') if subscription.end_date else 'N/A',
                'pricing_url': f"{current_app.config['BASE_URL']}/pricing"
            }
            
            # Send email
            EmailService.send_subscription_expiring_email(admin_user, school, plan, email_data)
            return True
            
        except Exception as e:
            print(f"Error sending expiration warning email: {e}")
            return False
    
    def send_expired_notification_email(self, school_id):
        """
        Send subscription expired notification email
        """
        try:
            from email_service import EmailService
            from datetime import datetime
            
            school = School.query.get(school_id)
            if not school:
                return False
            
            # Get admin user
            admin_user = User.query.filter_by(
                school_id=school_id,
                role='school_admin'
            ).first()
            
            if not admin_user:
                return False
            
            # Get subscription details
            subscription = SchoolSubscription.query.filter_by(
                school_id=school_id,
                status='expired'
            ).first()
            
            if not subscription:
                return False
            
            plan = SubscriptionPlan.query.get(subscription.plan_id)
            if not plan:
                return False
            
            # Prepare email data
            email_data = {
                'admin_name': f"{admin_user.first_name} {admin_user.last_name}",
                'admin_email': admin_user.email,
                'school_name': school.name,
                'school_code': school.code,
                'plan_name': plan.name,
                'expiry_date': subscription.end_date.strftime('%B %d, %Y') if subscription.end_date else 'N/A',
                'pricing_url': f"{current_app.config['BASE_URL']}/pricing"
            }
            
            # Send email
            EmailService.send_subscription_expired_email(admin_user, school, plan, email_data)
            return True
            
        except Exception as e:
            print(f"Error sending expired notification email: {e}")
            return False

    def create_default_plans(self):
        """
        Create default subscription plans if they don't exist
        """
        from app import db, SubscriptionPlan
        
        plans = [
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
        
        for plan_data in plans:
            existing_plan = SubscriptionPlan.query.filter_by(name=plan_data['name']).first()
            if not existing_plan:
                plan = SubscriptionPlan(**plan_data)
                db.session.add(plan)
        
        db.session.commit()
        return True
