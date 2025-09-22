#!/usr/bin/env python3
"""
Email Service for Student Assignment Tracking App
Handles all email operations including notifications, password resets, and system emails
"""

from flask import current_app, render_template
from flask_mail import Mail, Message
from threading import Thread
import os

# Initialize Flask-Mail
mail = Mail()

def init_mail(app):
    """Initialize Flask-Mail with the Flask app"""
    mail.init_app(app)

def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        try:
            mail.send(msg)
            print(f"Email sent successfully to {msg.recipients}")
        except Exception as e:
            print(f"Failed to send email: {str(e)}")

def send_email(subject, recipients, template, **kwargs):
    """Send email with template"""
    try:
        msg = Message(
            subject=subject,
            recipients=recipients,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER')
        )
        
        # Render HTML template
        msg.html = render_template(f'emails/{template}.html', **kwargs)
        
        # Send email asynchronously
        Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
        
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

class EmailService:
    """Email service class for handling different types of emails"""
    
    @staticmethod
    def send_welcome_email(user, school=None, username=None, password=None):
        """Send welcome email to new user"""
        subject = f"Welcome to {school.name if school else 'EduTrack'}!"
        return send_email(
            subject=subject,
            recipients=[user.email],
            template='welcome',
            user=user,
            school=school,
            username=username or user.username,
            password=password
        )
    
    @staticmethod
    def send_school_registration_confirmation(school, admin):
        """Send confirmation email after school registration"""
        subject = f"School Registration Confirmed - {school.name}"
        return send_email(
            subject=subject,
            recipients=[admin.email],
            template='school_registration',
            school=school,
            admin=admin
        )
    
    @staticmethod
    def send_password_reset_email(user, reset_token, new_password=None):
        """Send password reset email"""
        subject = "Password Reset - EduTrack"
        reset_url = f"{current_app.config.get('BASE_URL', 'http://127.0.0.1:5000')}/reset-password/{reset_token}"
        return send_email(
            subject=subject,
            recipients=[user.email],
            template='password_reset',
            user=user,
            reset_url=reset_url,
            new_password=new_password
        )
    
    @staticmethod
    def send_assignment_notification(student, assignment, teacher):
        """Send assignment notification to parent"""
        subject = f"New Assignment: {assignment.title}"
        return send_email(
            subject=subject,
            recipients=[student.parent.email if student.parent else []],
            template='assignment_notification',
            student=student,
            assignment=assignment,
            teacher=teacher
        )
    
    @staticmethod
    def send_assignment_submission_notification(teacher, student, assignment):
        """Send notification when student submits assignment"""
        subject = f"Assignment Submitted: {assignment.title}"
        return send_email(
            subject=subject,
            recipients=[teacher.email],
            template='assignment_submission',
            teacher=teacher,
            student=student,
            assignment=assignment
        )
    
    @staticmethod
    def send_grade_notification(student, assignment, grade):
        """Send grade notification to parent"""
        subject = f"Grade Posted: {assignment.title}"
        return send_email(
            subject=subject,
            recipients=[student.parent.email if student.parent else []],
            template='grade_notification',
            student=student,
            assignment=assignment,
            grade=grade
        )
    
    @staticmethod
    def send_lesson_notification(student, lesson, teacher):
        """Send lesson notification to parent"""
        subject = f"New Lesson: {lesson.title}"
        return send_email(
            subject=subject,
            recipients=[student.parent.email if student.parent else []],
            template='lesson_notification',
            student=student,
            lesson=lesson,
            teacher=teacher
        )
    
    @staticmethod
    def send_system_notification(recipients, subject, message, notification_type='info'):
        """Send system-wide notification"""
        return send_email(
            subject=f"[EduTrack] {subject}",
            recipients=recipients,
            template='system_notification',
            message=message,
            notification_type=notification_type
        )
    
    @staticmethod
    def send_parent_invitation(parent_email, student, school):
        """Send parent invitation email"""
        subject = f"Parent Invitation - {school.name}"
        return send_email(
            subject=subject,
            recipients=[parent_email],
            template='parent_invitation',
            student=student,
            school=school
        )

    @staticmethod
    def send_subscription_welcome_email(admin_user, school, plan, email_data, username=None, password=None):
        """Send welcome email to new subscriber"""
        try:
            # Add username and password to email data
            email_data['username'] = username or admin_user.username
            email_data['password'] = password
            
            send_email(
                subject=f"🎉 Welcome to Home Task Tracker - {plan.name} Activated!",
                recipients=[admin_user.email],
                template='subscription_welcome',
                **email_data
            )
            print(f"✅ Welcome email sent to {admin_user.email}")
            return True
        except Exception as e:
            print(f"❌ Failed to send welcome email: {str(e)}")
            return False

    @staticmethod
    def send_subscription_expiring_email(admin_user, school, plan, email_data):
        """Send subscription expiring warning email"""
        try:
            send_email(
                subject=f"⚠️ Subscription Expiring Soon - {plan.name}",
                recipients=[admin_user.email],
                template='subscription_expiring',
                **email_data
            )
            print(f"✅ Expiration warning email sent to {admin_user.email}")
            return True
        except Exception as e:
            print(f"❌ Failed to send expiration warning email: {str(e)}")
            return False

def test_email_configuration():
    """Test email configuration"""
    try:
        with current_app.app_context():
            # Test email configuration
            print("Testing email configuration...")
            print(f"MAIL_SERVER: {current_app.config.get('MAIL_SERVER')}")
            print(f"MAIL_PORT: {current_app.config.get('MAIL_PORT')}")
            print(f"MAIL_USE_TLS: {current_app.config.get('MAIL_USE_TLS')}")
            print(f"MAIL_USERNAME: {current_app.config.get('MAIL_USERNAME')}")
            print(f"MAIL_DEFAULT_SENDER: {current_app.config.get('MAIL_DEFAULT_SENDER')}")
            
            # Send test email
            test_msg = Message(
                subject="EduTrack Email Test",
                recipients=[current_app.config.get('MAIL_DEFAULT_SENDER')],
                sender=current_app.config.get('MAIL_DEFAULT_SENDER'),
                body="This is a test email from EduTrack system."
            )
            
            mail.send(test_msg)
            print("✅ Email configuration test successful!")
            return True
            
    except Exception as e:
        print(f"❌ Email configuration test failed: {str(e)}")
        return False