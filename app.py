from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, date, timedelta
import os
import secrets
import string
import threading
import time
import schedule
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///edutrack.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, teacher, parent
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    profile_picture = db.Column(db.String(200), nullable=True)  # Path to profile picture
    is_active = db.Column(db.Boolean, default=True)  # For teacher activation/deactivation
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    classes = db.relationship('Class', backref='teacher', lazy=True)
    students = db.relationship('Student', backref='parent', lazy=True)
    assignments = db.relationship('Assignment', backref='teacher', lazy=True)
    comments_given = db.relationship('Comment', foreign_keys='Comment.giver_id', backref='giver', lazy=True)
    comments_received = db.relationship('Comment', foreign_keys='Comment.receiver_id', backref='receiver', lazy=True)
    
    def is_active_user(self):
        """Check if user is active (for teacher activation/deactivation)"""
        return self.is_active

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    grade_level = db.Column(db.String(20), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    students = db.relationship('Student', backref='class_obj', lazy=True)
    subjects = db.relationship('Subject', backref='class_obj', lazy=True)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    assignments = db.relationship('Assignment', backref='subject', lazy=True)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    date_of_birth = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    assignment_records = db.relationship('AssignmentRecord', backref='student', lazy=True)
    
    @staticmethod
    def generate_student_id():
        """Generate a unique student ID"""
        import random
        year = datetime.now().year
        # Generate a 4-digit random number
        random_num = random.randint(1000, 9999)
        student_id = f"STU{year}{random_num}"
        
        # Ensure uniqueness
        while Student.query.filter_by(student_id=student_id).first():
            random_num = random.randint(1000, 9999)
            student_id = f"STU{year}{random_num}"
        
        return student_id
    comments = db.relationship('Comment', foreign_keys='Comment.student_id', backref='student', lazy=True)

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    assignment_records = db.relationship('AssignmentRecord', backref='assignment', lazy=True)

class AssignmentRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    submitted_date = db.Column(db.Date)
    grade = db.Column(db.String(10))  # A, B, C, D, F, or percentage
    feedback = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure unique combination of student and assignment
    __table_args__ = (db.UniqueConstraint('student_id', 'assignment_id', name='unique_student_assignment'),)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    giver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # For teacher-to-teacher comments
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=True)  # For student-specific comments
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=True)  # For assignment-specific comments
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    assignment = db.relationship('Assignment', backref='comments', lazy=True)

class HomeworkRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    week = db.Column(db.String(50), nullable=False)  # e.g., "Week 1", "Week 2", etc.
    description = db.Column(db.Text, nullable=False)  # Description of homework given
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    class_obj = db.relationship('Class', backref='homework_records', lazy=True)
    teacher = db.relationship('User', backref='homework_records', lazy=True)
    comments = db.relationship('HomeworkComment', backref='homework_record', lazy=True, cascade='all, delete-orphan')

class HomeworkComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    homework_record_id = db.Column(db.Integer, db.ForeignKey('homework_record.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    admin = db.relationship('User', backref='homework_comments', lazy=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # None for broadcast to all teachers
    subject = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    parent_message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=True)  # For replies
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages', lazy=True)
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages', lazy=True)
    parent_message = db.relationship('Message', remote_side=[id], backref='replies', lazy=True)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=True)
    type = db.Column(db.String(50), nullable=False)  # 'message_reply', 'new_message', etc.
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='notifications', lazy=True)
    message = db.relationship('Message', backref='notifications', lazy=True)

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    week = db.Column(db.String(50), nullable=False)  # e.g., "Week 1", "Week 2", etc.
    term = db.Column(db.String(20), nullable=False)  # e.g., "First Term", "Second Term", "Third Term"
    session = db.Column(db.String(20), nullable=False)  # e.g., "2024/2025"
    
    # Lesson Plan Fields
    objectives = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=True)  # Rich text content for lesson plan
    activities = db.Column(db.Text, nullable=True)
    resources = db.Column(db.Text, nullable=True)
    assessment = db.Column(db.Text, nullable=True)
    
    # Lesson Note Fields
    lesson_notes = db.Column(db.Text, nullable=True)  # Rich text content for lesson notes
    student_attendance = db.Column(db.Text, nullable=True)  # Track attendance
    student_performance = db.Column(db.Text, nullable=True)  # Track student performance
    challenges = db.Column(db.Text, nullable=True)  # Challenges encountered
    next_steps = db.Column(db.Text, nullable=True)  # Next steps for improvement
    
    # Status and Progress
    status = db.Column(db.String(20), default='planned')  # planned, in_progress, completed
    completion_percentage = db.Column(db.Integer, default=0)  # 0-100%
    
    # Timestamps
    planned_date = db.Column(db.Date, nullable=True)  # When lesson is planned for
    taught_date = db.Column(db.Date, nullable=True)  # When lesson was actually taught
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subject = db.relationship('Subject', backref='lessons', lazy=True)
    teacher = db.relationship('User', backref='lessons', lazy=True)
    attachments = db.relationship('LessonAttachment', backref='lesson', lazy=True, cascade='all, delete-orphan')

class LessonAttachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # pdf, doc, docx, jpg, png
    file_size = db.Column(db.Integer, nullable=False)  # in bytes
    attachment_type = db.Column(db.String(20), nullable=False)  # plan, note, resource, assessment
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class LessonComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lesson = db.relationship('Lesson', backref='comments')
    admin = db.relationship('User', backref='lesson_comments')
    
    def __repr__(self):
        return f'<LessonComment {self.id}>'

class SystemSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Utility functions
def generate_password(length=8):
    """Generate a random password"""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Template context processors
@app.context_processor
def inject_globals():
    return {
        'date': date,
        'datetime': datetime
    }

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'teacher':
            return redirect(url_for('teacher_dashboard'))
        elif current_user.role == 'parent':
            return redirect(url_for('parent_dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact the administrator.', 'error')
                return render_template('auth/login.html')
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('auth/login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Get statistics
    total_students = Student.query.count()
    total_teachers = User.query.filter_by(role='teacher').count()
    total_classes = Class.query.count()
    recent_assignments = Assignment.query.order_by(Assignment.created_at.desc()).limit(5).all()
    
    # Get recent lesson submissions
    recent_lessons = Lesson.query.order_by(Lesson.created_at.desc()).limit(5).all()
    
    # Get teachers with their submission counts
    teachers = User.query.filter_by(role='teacher').all()
    teachers_with_submissions = []
    
    for teacher in teachers:
        homework_count = HomeworkRecord.query.filter_by(teacher_id=teacher.id).count()
        lesson_count = Lesson.query.filter_by(teacher_id=teacher.id).count()
        
        teachers_with_submissions.append({
            'teacher': teacher,
            'homework_count': homework_count,
            'lesson_count': lesson_count,
            'total_submissions': homework_count + lesson_count
        })
    
    # Get recent notifications
    recent_notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(5).all()
    unread_notifications_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    
    return render_template('admin/dashboard.html', 
                         total_students=total_students,
                         total_teachers=total_teachers,
                         total_classes=total_classes,
                         recent_assignments=recent_assignments,
                         recent_lessons=recent_lessons,
                         teachers_with_submissions=teachers_with_submissions,
                         recent_notifications=recent_notifications,
                         unread_notifications_count=unread_notifications_count)

@app.route('/api/admin/dashboard-data')
@login_required
def api_admin_dashboard_data():
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    # Get fresh data
    recent_assignments = Assignment.query.order_by(Assignment.created_at.desc()).limit(5).all()
    
    # Get teachers with their submission counts
    teachers = User.query.filter_by(role='teacher').all()
    teachers_with_submissions = []
    
    for teacher in teachers:
        homework_count = HomeworkRecord.query.filter_by(teacher_id=teacher.id).count()
        lesson_count = Lesson.query.filter_by(teacher_id=teacher.id).count()
        
        teachers_with_submissions.append({
            'teacher': {
                'first_name': teacher.first_name,
                'last_name': teacher.last_name,
                'email': teacher.email,
                'classes': [{'name': cls.name} for cls in teacher.classes]
            },
            'homework_count': homework_count,
            'lesson_count': lesson_count,
            'total_submissions': homework_count + lesson_count
        })
    
    return jsonify({
        'teachers_with_submissions': teachers_with_submissions,
        'recent_assignments': [
            {
                'id': assignment.id,
                'title': assignment.title,
                'subject': {'name': assignment.subject.name},
                'teacher': {
                    'first_name': assignment.teacher.first_name,
                    'last_name': assignment.teacher.last_name
                },
                'due_date': assignment.due_date.strftime('%Y-%m-%d')
            } for assignment in recent_assignments
        ]
    })

@app.route('/api/teacher/dashboard-data')
@login_required
def api_teacher_dashboard_data():
    if current_user.role != 'teacher':
        return jsonify({'error': 'Access denied'}), 403
    
    # Get teacher's classes with fresh data
    classes = Class.query.filter_by(teacher_id=current_user.id).all()
    classes_data = []
    
    for class_obj in classes:
        classes_data.append({
            'id': class_obj.id,
            'name': class_obj.name,
            'grade_level': class_obj.grade_level,
            'student_count': len(class_obj.students),
            'subject_count': len(class_obj.subjects)
        })
    
    # Get recent assignments
    recent_assignments = Assignment.query.filter_by(teacher_id=current_user.id).order_by(Assignment.created_at.desc()).limit(5).all()
    assignments_data = []
    
    for assignment in recent_assignments:
        assignments_data.append({
            'id': assignment.id,
            'title': assignment.title,
            'subject': {'name': assignment.subject.name},
            'due_date': assignment.due_date.strftime('%Y-%m-%d'),
            'created_at': assignment.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    # Get recent admin comments
    recent_comments = LessonComment.query.join(Lesson).filter(
        Lesson.teacher_id == current_user.id
    ).order_by(LessonComment.created_at.desc()).limit(5).all()
    
    comments_data = []
    for comment in recent_comments:
        comments_data.append({
            'id': comment.id,
            'comment': comment.comment,
            'lesson': {
                'id': comment.lesson.id,
                'title': comment.lesson.title
            },
            'admin': {
                'first_name': comment.admin.first_name,
                'last_name': comment.admin.last_name
            },
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return jsonify({
        'classes': classes_data,
        'recent_assignments': assignments_data,
        'recent_comments': comments_data
    })

@app.route('/api/parent/dashboard-data')
@login_required
def api_parent_dashboard_data():
    if current_user.role != 'parent':
        return jsonify({'error': 'Access denied'}), 403
    
    # Get parent's children with fresh assignment data
    children = Student.query.filter_by(parent_id=current_user.id).all()
    children_data = []
    
    for child in children:
        assignment_records_list = child.assignment_records
        total_assignments = len(assignment_records_list)
        completed_assignments = len([r for r in assignment_records_list if r.completed])
        completion_rate = (completed_assignments / total_assignments * 100) if total_assignments > 0 else 0
        pending_assignments = total_assignments - completed_assignments
        
        children_data.append({
            'id': child.id,
            'first_name': child.first_name,
            'last_name': child.last_name,
            'student_id': child.student_id,
            'class_name': child.class_obj.name if child.class_obj else 'No Class Assigned',
            'total_assignments': total_assignments,
            'completed_assignments': completed_assignments,
            'pending_assignments': pending_assignments,
            'completion_rate': completion_rate
        })
    
    # Get recent assignment records for all children
    recent_records = []
    for child in children:
        child_records = AssignmentRecord.query.filter_by(student_id=child.id).order_by(AssignmentRecord.created_at.desc()).limit(5).all()
        recent_records.extend(child_records)
    
    # Sort by creation date and limit to 10 most recent
    recent_records.sort(key=lambda x: x.created_at, reverse=True)
    recent_records = recent_records[:10]
    
    records_data = []
    for record in recent_records:
        records_data.append({
            'id': record.id,
            'assignment': {
                'title': record.assignment.title,
                'subject': record.assignment.subject.name
            },
            'student': {
                'first_name': record.student.first_name,
                'last_name': record.student.last_name
            },
            'completed': record.completed,
            'grade': record.grade,
            'submitted_date': record.submitted_date.strftime('%Y-%m-%d') if record.submitted_date else None,
            'created_at': record.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return jsonify({
        'children': children_data,
        'recent_records': records_data
    })

@app.route('/admin/lesson-submissions')
@login_required
def admin_lesson_submissions():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Get filter parameters
    teacher_filter = request.args.get('teacher_filter', '')
    week_filter = request.args.get('week_filter', '')
    term_filter = request.args.get('term_filter', '')
    status_filter = request.args.get('status_filter', '')
    
    # Build query
    query = Lesson.query
    
    if teacher_filter:
        query = query.filter(Lesson.teacher_id == teacher_filter)
    if week_filter:
        query = query.filter(Lesson.week == week_filter)
    if term_filter:
        query = query.filter(Lesson.term == term_filter)
    if status_filter:
        query = query.filter(Lesson.status == status_filter)
    
    lessons = query.order_by(Lesson.created_at.desc()).all()
    
    # Get teachers for filter dropdown
    teachers = User.query.filter_by(role='teacher').all()
    
    # Get unique weeks and terms for filter dropdowns
    weeks = db.session.query(Lesson.week).distinct().all()
    weeks = [week[0] for week in weeks if week[0]]
    
    terms = db.session.query(Lesson.term).distinct().all()
    terms = [term[0] for term in terms if term[0]]
    
    return render_template('admin/lesson_submissions.html',
                         lessons=lessons,
                         teachers=teachers,
                         weeks=weeks,
                         terms=terms,
                         teacher_filter=teacher_filter,
                         week_filter=week_filter,
                         term_filter=term_filter,
                         status_filter=status_filter)

@app.route('/admin/lesson/<int:lesson_id>')
@login_required
def admin_view_lesson(lesson_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    lesson = Lesson.query.get_or_404(lesson_id)
    return render_template('admin/view_lesson.html', lesson=lesson)

@app.route('/admin/lesson/<int:lesson_id>/comment', methods=['POST'])
@login_required
def admin_add_lesson_comment(lesson_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    lesson = Lesson.query.get_or_404(lesson_id)
    comment_text = request.form.get('comment', '').strip()
    
    if not comment_text:
        flash('Comment cannot be empty', 'error')
        return redirect(url_for('admin_view_lesson', lesson_id=lesson_id))
    
    # Create new comment
    comment = LessonComment(
        lesson_id=lesson_id,
        admin_id=current_user.id,
        comment=comment_text
    )
    
    try:
        db.session.add(comment)
        db.session.commit()
        flash('Comment added successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error adding comment', 'error')
    
    return redirect(url_for('admin_view_lesson', lesson_id=lesson_id))

@app.route('/admin/lesson/<int:lesson_id>/comment/<int:comment_id>/edit', methods=['POST'])
@login_required
def admin_edit_lesson_comment(lesson_id, comment_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    comment = LessonComment.query.get_or_404(comment_id)
    if comment.admin_id != current_user.id:
        flash('You can only edit your own comments', 'error')
        return redirect(url_for('admin_view_lesson', lesson_id=lesson_id))
    
    comment_text = request.form.get('comment', '').strip()
    if not comment_text:
        flash('Comment cannot be empty', 'error')
        return redirect(url_for('admin_view_lesson', lesson_id=lesson_id))
    
    try:
        comment.comment = comment_text
        comment.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Comment updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating comment', 'error')
    
    return redirect(url_for('admin_view_lesson', lesson_id=lesson_id))

@app.route('/admin/lesson/<int:lesson_id>/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def admin_delete_lesson_comment(lesson_id, comment_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    comment = LessonComment.query.get_or_404(comment_id)
    if comment.admin_id != current_user.id:
        flash('You can only delete your own comments', 'error')
        return redirect(url_for('admin_view_lesson', lesson_id=lesson_id))
    
    try:
        db.session.delete(comment)
        db.session.commit()
        flash('Comment deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting comment', 'error')
    
    return redirect(url_for('admin_view_lesson', lesson_id=lesson_id))

@app.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Get teacher's classes
    classes = Class.query.filter_by(teacher_id=current_user.id).all()
    recent_assignments = Assignment.query.filter_by(teacher_id=current_user.id).order_by(Assignment.created_at.desc()).limit(5).all()
    
    # Get recent admin comments on teacher's lessons
    recent_comments = LessonComment.query.join(Lesson).filter(
        Lesson.teacher_id == current_user.id
    ).order_by(LessonComment.created_at.desc()).limit(5).all()
    
    return render_template('teacher/dashboard.html', 
                         classes=classes, 
                         recent_assignments=recent_assignments,
                         recent_comments=recent_comments)

@app.route('/parent/dashboard')
@login_required
def parent_dashboard():
    if current_user.role != 'parent':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Get parent's children with their assignment records
    children = Student.query.filter_by(parent_id=current_user.id).all()
    
    # Get recent assignment records for all children
    recent_records = []
    for child in children:
        child_records = AssignmentRecord.query.filter_by(student_id=child.id).order_by(AssignmentRecord.created_at.desc()).limit(5).all()
        recent_records.extend(child_records)
    
    # Sort by creation date and limit to 10 most recent
    recent_records.sort(key=lambda x: x.created_at, reverse=True)
    recent_records = recent_records[:10]
    
    # Get school information
    school_name = get_setting('school_name', 'EduTrack School')
    school_code = get_setting('school_code', 'ETS001')
    school_address = get_setting('school_address', '')
    school_phone = get_setting('school_phone', '')
    school_email = get_setting('school_email', '')
    school_website = get_setting('school_website', '')
    
    return render_template('parent/dashboard.html', 
                         children=children, 
                         recent_records=recent_records,
                         school_name=school_name,
                         school_code=school_code,
                         school_address=school_address,
                         school_phone=school_phone,
                         school_email=school_email,
                         school_website=school_website)

# Additional routes for admin functionality
@app.route('/admin/teachers')
@login_required
def manage_teachers():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    teachers = User.query.filter_by(role='teacher').all()
    return render_template('admin/teachers.html', teachers=teachers)

@app.route('/admin/classes')
@login_required
def manage_classes():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    classes = Class.query.all()
    return render_template('admin/classes.html', classes=classes)

@app.route('/admin/class/<int:class_id>')
@login_required
def admin_view_class(class_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    class_obj = Class.query.get_or_404(class_id)
    
    # Get class statistics
    total_students = len(class_obj.students)
    total_subjects = len(class_obj.subjects)
    recent_assignments = Assignment.query.join(Subject).filter(Subject.class_id == class_id).order_by(Assignment.created_at.desc()).limit(5).all()
    recent_homework_records = HomeworkRecord.query.filter_by(class_id=class_id).order_by(HomeworkRecord.created_at.desc()).limit(5).all()
    
    return render_template('admin/class_detail.html', 
                         class_obj=class_obj, 
                         total_students=total_students,
                         total_subjects=total_subjects,
                         recent_assignments=recent_assignments,
                         recent_homework_records=recent_homework_records)

@app.route('/admin/reports')
@login_required
def view_reports():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Get filter parameters
    class_filter = request.args.get('class_filter', '')
    
    # Get all classes for filter dropdown
    all_classes = Class.query.all()
    
    # Get statistics
    total_students = Student.query.count()
    total_teachers = User.query.filter_by(role='teacher').count()
    total_classes = Class.query.count()
    
    # Calculate assignment completion rate
    total_assignments = Assignment.query.count()
    completed_assignments = AssignmentRecord.query.filter_by(completed=True).count()
    completion_rate = (completed_assignments / total_assignments * 100) if total_assignments > 0 else 0
    
    # Get class overview data
    class_overview = []
    for class_obj in all_classes:
        if not class_filter or str(class_obj.id) == class_filter:
            student_count = len(class_obj.students)
            class_overview.append({
                'name': class_obj.name,
                'grade_level': class_obj.grade_level,
                'student_count': student_count,
                'teacher_name': f"{class_obj.teacher.first_name} {class_obj.teacher.last_name}" if class_obj.teacher else "No Teacher"
            })
    
    # Get recent activity
    recent_assignments = Assignment.query.order_by(Assignment.created_at.desc()).limit(5).all()
    recent_homework_records = HomeworkRecord.query.order_by(HomeworkRecord.created_at.desc()).limit(5).all()
    
    # Get teacher performance data
    teachers = User.query.filter_by(role='teacher').all()
    teacher_performance = []
    
    for teacher in teachers:
        # Count submissions
        homework_count = HomeworkRecord.query.filter_by(teacher_id=teacher.id).count()
        lesson_count = Lesson.query.filter_by(teacher_id=teacher.id).count()
        total_submissions = homework_count + lesson_count
        
        # Calculate performance score (based on submission frequency)
        # Assuming 13 weeks per term, 3 terms per year = 39 weeks
        # Expected: 1 homework record per week + 1 lesson per week = 78 submissions per year
        # For current term (13 weeks): 26 expected submissions
        weeks_in_term = 13
        expected_homework = weeks_in_term
        expected_lessons = weeks_in_term
        expected_total = expected_homework + expected_lessons
        
        performance_score = (total_submissions / expected_total * 100) if expected_total > 0 else 0
        
        # Get recent activity (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_homework = HomeworkRecord.query.filter(
            HomeworkRecord.teacher_id == teacher.id,
            HomeworkRecord.created_at >= thirty_days_ago
        ).count()
        recent_lessons = Lesson.query.filter(
            Lesson.teacher_id == teacher.id,
            Lesson.created_at >= thirty_days_ago
        ).count()
        
        # Determine performance status
        if performance_score >= 80:
            status = 'excellent'
            status_text = 'Excellent'
        elif performance_score >= 60:
            status = 'good'
            status_text = 'Good'
        elif performance_score >= 40:
            status = 'fair'
            status_text = 'Fair'
        else:
            status = 'needs_improvement'
            status_text = 'Needs Improvement'
        
        teacher_performance.append({
            'teacher': teacher,
            'homework_count': homework_count,
            'lesson_count': lesson_count,
            'total_submissions': total_submissions,
            'performance_score': performance_score,
            'status': status,
            'status_text': status_text,
            'recent_homework': recent_homework,
            'recent_lessons': recent_lessons,
            'classes': [cls.name for cls in teacher.classes]
        })
    
    # Sort by performance score (descending)
    teacher_performance.sort(key=lambda x: x['performance_score'], reverse=True)
    
    return render_template('admin/reports.html', 
                         all_classes=all_classes,
                         class_filter=class_filter,
                         total_students=total_students,
                         total_teachers=total_teachers,
                         total_classes=total_classes,
                         completion_rate=completion_rate,
                         class_overview=class_overview,
                         recent_assignments=recent_assignments,
                         recent_homework_records=recent_homework_records,
                         teacher_performance=teacher_performance)

@app.route('/admin/settings')
@login_required
def system_settings():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Get current settings from database
    settings = {
        'school_name': get_setting('school_name', 'EduTrack School'),
        'school_code': get_setting('school_code', 'ETS001'),
        'school_address': get_setting('school_address', '123 Education Street, Learning City, LC 12345'),
        'school_phone': get_setting('school_phone', '+1 (555) 123-4567'),
        'school_email': get_setting('school_email', 'info@edutrack.edu'),
        'school_website': get_setting('school_website', ''),
        'academic_year': get_setting('academic_year', '2024-2025'),
        'max_students_per_class': int(get_setting('max_students_per_class', '30')),
        'assignment_late_penalty': int(get_setting('assignment_late_penalty', '10')),
        'notification_email': get_setting('notification_email', 'true').lower() == 'true',
        'backup_frequency': get_setting('backup_frequency', 'daily'),
        'auto_backup_enabled': get_setting('auto_backup_enabled', 'false').lower() == 'true',
        'auto_backup_frequency': get_setting('auto_backup_frequency', 'daily'),
        'auto_backup_time': get_setting('auto_backup_time', '02:00'),
        'auto_backup_retention': int(get_setting('auto_backup_retention', '30'))
    }
    
    return render_template('admin/settings.html', settings=settings)

@app.route('/admin/settings', methods=['POST'])
@login_required
def update_settings():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Get form data
    school_name = request.form.get('school_name', '')
    school_code = request.form.get('school_code', '')
    school_address = request.form.get('school_address', '')
    school_phone = request.form.get('school_phone', '')
    school_email = request.form.get('school_email', '')
    school_website = request.form.get('school_website', '')
    academic_year = request.form.get('academic_year', '')
    max_students = request.form.get('max_students_per_class', 30)
    late_penalty = request.form.get('assignment_late_penalty', 10)
    notification_email = 'notification_email' in request.form
    backup_frequency = request.form.get('backup_frequency', 'daily')
    
    # Auto backup settings
    auto_backup_enabled = 'auto_backup_enabled' in request.form
    auto_backup_frequency = request.form.get('auto_backup_frequency', 'daily')
    auto_backup_time = request.form.get('auto_backup_time', '02:00')
    auto_backup_retention = request.form.get('auto_backup_retention', 30)
    
    # Validate data
    if not school_name or not school_code:
        flash('School name and code are required', 'error')
        return redirect(url_for('system_settings'))
    
    try:
        # Save settings to database
        set_setting('school_name', school_name)
        set_setting('school_code', school_code)
        set_setting('school_address', school_address)
        set_setting('school_phone', school_phone)
        set_setting('school_email', school_email)
        set_setting('school_website', school_website)
        set_setting('academic_year', academic_year)
        set_setting('max_students_per_class', str(max_students))
        set_setting('assignment_late_penalty', str(late_penalty))
        set_setting('notification_email', str(notification_email).lower())
        set_setting('backup_frequency', backup_frequency)
        
        # Save auto backup settings
        set_setting('auto_backup_enabled', str(auto_backup_enabled).lower())
        set_setting('auto_backup_frequency', auto_backup_frequency)
        set_setting('auto_backup_time', auto_backup_time)
        set_setting('auto_backup_retention', str(auto_backup_retention))
        
        # Reschedule auto backups if settings changed
        schedule_auto_backup()
        
        flash('Settings updated successfully!', 'success')
    except Exception as e:
        flash('Error updating settings. Please try again.', 'error')
        print(f"Error updating settings: {e}")
    
    return redirect(url_for('system_settings'))

@app.route('/admin/backup')
@login_required
def backup_data():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    try:
        import sqlite3
        import shutil
        from datetime import datetime
        from flask import send_file
        
        # Create backup directory if it doesn't exist
        backup_dir = 'backups'
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'edutrack_backup_{timestamp}.db'
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Copy the database file (it's in the instance folder)
        db_path = os.path.join('instance', 'edutrack.db')
        if not os.path.exists(db_path):
            flash('Database file not found', 'error')
            return redirect(url_for('system_settings'))
        
        shutil.copy2(db_path, backup_path)
        
        # Store backup info in settings
        backup_info = f"{backup_filename},{datetime.now().isoformat()}"
        set_setting('last_backup', backup_info)
        
        # Return the file for download
        return send_file(
            backup_path,
            as_attachment=True,
            download_name=backup_filename,
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        flash(f'Error creating backup: {str(e)}', 'error')
        print(f"Backup error: {e}")
        return redirect(url_for('system_settings'))

@app.route('/admin/backups')
@login_required
def list_backups():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    try:
        import os
        from datetime import datetime
        
        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            return jsonify({'backups': []})
        
        # Get all backup files
        backup_files = []
        for filename in os.listdir(backup_dir):
            if filename.endswith('.db') and filename.startswith('edutrack_backup_'):
                file_path = os.path.join(backup_dir, filename)
                file_stat = os.stat(file_path)
                file_size = file_stat.st_size
                file_date = datetime.fromtimestamp(file_stat.st_mtime)
                
                backup_files.append({
                    'filename': filename,
                    'size': file_size,
                    'created': file_date.isoformat(),
                    'size_mb': round(file_size / (1024 * 1024), 2)
                })
        
        # Sort by creation date (newest first)
        backup_files.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({'backups': backup_files})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/backup/<filename>')
@login_required
def download_backup(filename):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    try:
        from flask import send_file
        import os
        
        # Security check - only allow .db files that start with edutrack_backup_
        if not filename.endswith('.db') or not filename.startswith('edutrack_backup_'):
            flash('Invalid backup file', 'error')
            return redirect(url_for('system_settings'))
        
        backup_path = os.path.join('backups', filename)
        if not os.path.exists(backup_path):
            flash('Backup file not found', 'error')
            return redirect(url_for('system_settings'))
        
        return send_file(
            backup_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        flash(f'Error downloading backup: {str(e)}', 'error')
        return redirect(url_for('system_settings'))

def create_auto_backup():
    """Create an automatic backup without user interaction"""
    try:
        import shutil
        from datetime import datetime
        
        # Create backup directory if it doesn't exist
        backup_dir = 'backups'
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'edutrack_auto_backup_{timestamp}.db'
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Copy the database file (it's in the instance folder)
        db_path = os.path.join('instance', 'edutrack.db')
        if not os.path.exists(db_path):
            print("Auto backup failed: Database file not found")
            return False
        
        shutil.copy2(db_path, backup_path)
        
        # Store backup info in settings
        backup_info = f"{backup_filename},{datetime.now().isoformat()}"
        set_setting('last_auto_backup', backup_info)
        
        print(f"Auto backup created successfully: {backup_filename}")
        
        # Clean up old backups based on retention policy
        cleanup_old_backups()
        
        return True
        
    except Exception as e:
        print(f"Auto backup error: {e}")
        return False

def cleanup_old_backups():
    """Remove old backup files based on retention policy"""
    try:
        import os
        from datetime import datetime, timedelta
        
        # Get retention days from settings
        retention_days = int(get_setting('auto_backup_retention', '30'))
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            return
        
        # Get all auto backup files
        for filename in os.listdir(backup_dir):
            if filename.startswith('edutrack_auto_backup_') and filename.endswith('.db'):
                file_path = os.path.join(backup_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                # Delete if older than retention period
                if file_time < cutoff_date:
                    os.remove(file_path)
                    print(f"Deleted old backup: {filename}")
                    
    except Exception as e:
        print(f"Error cleaning up old backups: {e}")

def create_notification(user_id, notification_type, title, content, message_id=None):
    """Create a notification for a user"""
    try:
        notification = Notification(
            user_id=user_id,
            message_id=message_id,
            type=notification_type,
            title=title,
            content=content
        )
        db.session.add(notification)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error creating notification: {e}")
        return False

def schedule_auto_backup():
    """Schedule automatic backups based on settings"""
    try:
        # Clear existing schedules
        schedule.clear()
        
        # Check if auto backup is enabled
        if not get_setting('auto_backup_enabled', 'false').lower() == 'true':
            print("Auto backup is disabled")
            return
        
        # Get backup settings
        frequency = get_setting('auto_backup_frequency', 'daily')
        backup_time = get_setting('auto_backup_time', '02:00')
        
        # Schedule based on frequency
        if frequency == 'daily':
            schedule.every().day.at(backup_time).do(create_auto_backup)
            print(f"Auto backup scheduled daily at {backup_time}")
        elif frequency == 'weekly':
            schedule.every().monday.at(backup_time).do(create_auto_backup)
            print(f"Auto backup scheduled weekly on Monday at {backup_time}")
        elif frequency == 'monthly':
            schedule.every().day.at(backup_time).do(lambda: create_auto_backup() if datetime.now().day == 1 else None)
            print(f"Auto backup scheduled monthly on 1st at {backup_time}")
            
    except Exception as e:
        print(f"Error scheduling auto backup: {e}")

def run_scheduler():
    """Run the scheduler in a background thread"""
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

@app.route('/admin/auto-backup/trigger', methods=['POST'])
@login_required
def trigger_auto_backup():
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        success = create_auto_backup()
        if success:
            return jsonify({'success': True, 'message': 'Auto backup created successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to create auto backup'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/admin/auto-backup/status')
@login_required
def auto_backup_status():
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Get auto backup settings
        enabled = get_setting('auto_backup_enabled', 'false').lower() == 'true'
        frequency = get_setting('auto_backup_frequency', 'daily')
        backup_time = get_setting('auto_backup_time', '02:00')
        retention = int(get_setting('auto_backup_retention', '30'))
        last_backup = get_setting('last_auto_backup', '')
        
        # Get backup count
        backup_dir = 'backups'
        auto_backup_count = 0
        if os.path.exists(backup_dir):
            auto_backup_count = len([f for f in os.listdir(backup_dir) if f.startswith('edutrack_auto_backup_') and f.endswith('.db')])
        
        return jsonify({
            'enabled': enabled,
            'frequency': frequency,
            'backup_time': backup_time,
            'retention_days': retention,
            'last_backup': last_backup,
            'auto_backup_count': auto_backup_count,
            'next_run': schedule.next_run().isoformat() if schedule.jobs else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/restore', methods=['POST'])
@login_required
def restore_data():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    try:
        import shutil
        from datetime import datetime
        
        # Get the most recent backup
        last_backup = get_setting('last_backup', '')
        if not last_backup:
            flash('No backup found to restore from', 'error')
            return redirect(url_for('system_settings'))
        
        backup_filename = last_backup.split(',')[0]
        backup_path = os.path.join('backups', backup_filename)
        
        if not os.path.exists(backup_path):
            flash('Backup file not found', 'error')
            return redirect(url_for('system_settings'))
        
        # Create a backup of current database before restore
        current_backup = f'edutrack_current_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        db_path = os.path.join('instance', 'edutrack.db')
        shutil.copy2(db_path, os.path.join('backups', current_backup))
        
        # Restore from backup
        shutil.copy2(backup_path, db_path)
        
        flash('Database restored successfully! Current database was backed up before restore.', 'success')
    except Exception as e:
        flash(f'Error restoring database: {str(e)}', 'error')
        print(f"Restore error: {e}")
    
    return redirect(url_for('system_settings'))

# Teacher routes
@app.route('/teacher/students')
@login_required
def manage_students():
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    class_id = request.args.get('class_id')
    if class_id:
        students = Student.query.filter_by(class_id=class_id).all()
    else:
        # Get students from all teacher's classes
        teacher_classes = Class.query.filter_by(teacher_id=current_user.id).all()
        class_ids = [c.id for c in teacher_classes]
        students = Student.query.filter(Student.class_id.in_(class_ids)).all()
    
    return render_template('teacher/students.html', students=students)

@app.route('/teacher/assignments')
@login_required
def manage_assignments():
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    assignments = Assignment.query.filter_by(teacher_id=current_user.id).all()
    print(f"DEBUG: Teacher ID: {current_user.id}, Found {len(assignments)} assignments")
    for assignment in assignments:
        print(f"DEBUG: Assignment: {assignment.title} (ID: {assignment.id})")
    return render_template('teacher/assignments.html', assignments=assignments)

@app.route('/teacher/class/create')
@login_required
def create_class():
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    return render_template('teacher/create_class.html')

@app.route('/teacher/assignment/create')
@login_required
def create_assignment():
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    return render_template('teacher/create_assignment.html')

# Parent routes
@app.route('/parent/child/<int:student_id>/progress')
@login_required
def child_progress(student_id):
    if current_user.role != 'parent':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    student = Student.query.get_or_404(student_id)
    if student.parent_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    return render_template('parent/child_progress.html', student=student)

# Assignment marking functionality
@app.route('/teacher/assignment/<int:assignment_id>/mark', methods=['POST'])
@login_required
def mark_assignment(assignment_id):
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.teacher_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    student_id = request.form.get('student_id')
    completed = request.form.get('completed') == 'on'
    grade = request.form.get('grade', '')
    feedback = request.form.get('feedback', '')
    
    # Find or create assignment record
    record = AssignmentRecord.query.filter_by(
        student_id=student_id, 
        assignment_id=assignment_id
    ).first()
    
    if not record:
        record = AssignmentRecord(
            student_id=student_id,
            assignment_id=assignment_id,
            completed=completed,
            grade=grade if grade else None,
            feedback=feedback if feedback else None
        )
        db.session.add(record)
    else:
        record.completed = completed
        record.grade = grade if grade else record.grade
        record.feedback = feedback if feedback else record.feedback
        if completed:
            record.submitted_date = date.today()
    
    db.session.commit()
    
    # Create notification for admin when assignment is marked
    admin_user = User.query.filter_by(role='admin').first()
    if admin_user:
        student = Student.query.get(student_id)
        status = "completed" if completed else "marked"
        create_notification(
            user_id=admin_user.id,
            notification_type='assignment_marked',
            title='Assignment Marked',
            content=f'Teacher {current_user.first_name} {current_user.last_name} marked assignment "{assignment.title}" for student {student.first_name} {student.last_name} as {status}'
        )
    
    flash('Assignment marked successfully!', 'success')
    return redirect(url_for('view_assignment', assignment_id=assignment_id))

# Parent registration functionality
@app.route('/teacher/register-parent', methods=['GET', 'POST'])
@login_required
def register_parent():
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        student_id = request.form['student_id']
        
        # Generate username and password
        username = f"{first_name.lower()}{last_name.lower()}{student_id}"
        password = generate_password()
        
        # Check if parent already exists
        if User.query.filter_by(email=email).first():
            flash('Parent with this email already exists', 'error')
            return redirect(url_for('register_parent'))
        
        # Create parent user
        parent = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role='parent',
            first_name=first_name,
            last_name=last_name
        )
        db.session.add(parent)
        db.session.flush()
        
        # Link student to parent
        student = Student.query.filter_by(student_id=student_id).first()
        if student:
            student.parent_id = parent.id
            db.session.commit()
            flash(f'Parent registered successfully! Username: {username}, Password: {password}', 'success')
        else:
            db.session.rollback()
            flash('Student not found', 'error')
    
    return render_template('teacher/register_parent.html')

# Password reset functionality
@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        
        if user:
            new_password = generate_password()
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            flash(f'Password reset successfully! Your new password is: {new_password}', 'success')
        else:
            flash('Email not found', 'error')
    
    return render_template('auth/reset_password.html')

# Profile picture upload
@app.route('/upload-profile-picture', methods=['POST'])
@login_required
def upload_profile_picture():
    if 'profile_picture' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('profile'))
    
    file = request.files['profile_picture']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('profile'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{current_user.id}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Update user profile picture
        current_user.profile_picture = f"uploads/{filename}"
        db.session.commit()
        
        flash('Profile picture updated successfully!', 'success')
    else:
        flash('Invalid file type. Please upload PNG, JPG, JPEG, or GIF files only.', 'error')
    
    return redirect(url_for('profile'))

# Teacher registration by admin
@app.route('/admin/register-teacher', methods=['GET', 'POST'])
@login_required
def register_teacher():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        
        # Generate username and password
        username = f"{first_name.lower()}{last_name.lower()}{secrets.randbelow(1000)}"
        password = generate_password()
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Teacher with this email already exists', 'error')
            return redirect(url_for('register_teacher'))
        
        # Create teacher user
        teacher = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role='teacher',
            first_name=first_name,
            last_name=last_name,
            is_active=True
        )
        db.session.add(teacher)
        db.session.commit()
        
        flash(f'Teacher registered successfully! Username: {username}, Password: {password}', 'success')
        return redirect(url_for('manage_teachers'))
    
    return render_template('admin/register_teacher.html')

# Teacher activation/deactivation
@app.route('/admin/teacher/<int:teacher_id>/toggle-status', methods=['POST'])
@login_required
def toggle_teacher_status(teacher_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    teacher = User.query.get_or_404(teacher_id)
    if teacher.role != 'teacher':
        flash('Invalid teacher', 'error')
        return redirect(url_for('manage_teachers'))
    
    teacher.is_active = not teacher.is_active
    db.session.commit()
    
    status = 'activated' if teacher.is_active else 'deactivated'
    flash(f'Teacher {teacher.first_name} {teacher.last_name} has been {status}', 'success')
    return redirect(url_for('manage_teachers'))

@app.route('/admin/teacher/<int:teacher_id>')
@login_required
def admin_view_teacher(teacher_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    teacher = User.query.get_or_404(teacher_id)
    if teacher.role != 'teacher':
        flash('Invalid teacher', 'error')
        return redirect(url_for('manage_teachers'))
    
    # Get teacher's classes, assignments, and homework records
    classes = Class.query.filter_by(teacher_id=teacher_id).all()
    assignments = Assignment.query.filter_by(teacher_id=teacher_id).order_by(Assignment.created_at.desc()).limit(10).all()
    homework_records = HomeworkRecord.query.filter_by(teacher_id=teacher_id).order_by(HomeworkRecord.created_at.desc()).limit(10).all()
    
    return render_template('admin/teacher_detail.html', 
                         teacher=teacher, 
                         classes=classes, 
                         assignments=assignments, 
                         homework_records=homework_records)

# Create class route (admin only)
@app.route('/admin/create-class', methods=['GET', 'POST'])
@login_required
def admin_create_class():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form['name']
        grade_level = request.form['grade_level']
        teacher_id = request.form.get('teacher_id')
        
        class_obj = Class(
            name=name,
            grade_level=grade_level,
            teacher_id=teacher_id if teacher_id else None
        )
        db.session.add(class_obj)
        db.session.commit()
        flash('Class created successfully!', 'success')
        return redirect(url_for('manage_classes'))
    
    teachers = User.query.filter_by(role='teacher', is_active=True).all()
    return render_template('admin/create_class.html', teachers=teachers)

# Create student route
@app.route('/teacher/create-student', methods=['GET', 'POST'])
@login_required
def create_student():
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        class_id = request.form['class_id']
        date_of_birth = request.form.get('date_of_birth')
        parent_email = request.form.get('parent_email')
        
        # Generate unique student ID
        student_id = Student.generate_student_id()
        
        # Create student
        student = Student(
            first_name=first_name,
            last_name=last_name,
            student_id=student_id,
            class_id=class_id,
            date_of_birth=datetime.strptime(date_of_birth, '%Y-%m-%d').date() if date_of_birth else None
        )
        db.session.add(student)
        db.session.flush()  # Get the student ID
        
        # If parent email provided, try to link to existing parent
        if parent_email:
            parent = User.query.filter_by(email=parent_email, role='parent').first()
            if parent:
                student.parent_id = parent.id
                db.session.commit()
                flash(f'Student created successfully! Student ID: {student_id}. Linked to parent: {parent.first_name} {parent.last_name}', 'success')
            else:
                db.session.commit()
                flash(f'Student created successfully! Student ID: {student_id}. No parent found with email: {parent_email}', 'warning')
        else:
            db.session.commit()
            flash(f'Student created successfully! Student ID: {student_id}', 'success')
        
        return redirect(url_for('manage_students'))
    
    # Get teacher's classes
    classes = Class.query.filter_by(teacher_id=current_user.id).all()
    return render_template('teacher/create_student.html', classes=classes)

# Student detail view route
@app.route('/teacher/student/<int:student_id>')
@login_required
def view_student(student_id):
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    student = Student.query.get_or_404(student_id)
    
    # Check if student belongs to teacher's class
    if student.class_obj.teacher_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('manage_students'))
    
    # Get student's assignment records
    assignment_records = AssignmentRecord.query.filter_by(student_id=student_id).all()
    
    return render_template('teacher/view_student.html', student=student, assignment_records=assignment_records)

# Edit student route
@app.route('/teacher/student/<int:student_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_student(student_id):
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    student = Student.query.get_or_404(student_id)
    
    # Check if student belongs to teacher's class
    if student.class_obj.teacher_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('manage_students'))
    
    if request.method == 'POST':
        student.first_name = request.form['first_name']
        student.last_name = request.form['last_name']
        student.class_id = request.form['class_id']
        student.date_of_birth = request.form.get('date_of_birth') if request.form.get('date_of_birth') else None
        student.parent_email = request.form.get('parent_email')
        
        try:
            db.session.commit()
            flash('Student updated successfully!', 'success')
            return redirect(url_for('manage_students'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating student. Please try again.', 'error')
    
    # Get teacher's classes for the dropdown
    classes = Class.query.filter_by(teacher_id=current_user.id).all()
    
    return render_template('teacher/edit_student.html', student=student, classes=classes)

# Delete student route
@app.route('/teacher/student/<int:student_id>/delete', methods=['POST'])
@login_required
def delete_student(student_id):
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    student = Student.query.get_or_404(student_id)
    
    # Check if student belongs to teacher's class
    if student.class_obj.teacher_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('manage_students'))
    
    try:
        # Delete related assignment records first
        AssignmentRecord.query.filter_by(student_id=student_id).delete()
        
        # Delete the student
        db.session.delete(student)
        db.session.commit()
        flash('Student deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting student. Please try again.', 'error')
    
    return redirect(url_for('manage_students'))

# Subject management routes
@app.route('/teacher/subjects')
@login_required
def manage_subjects():
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Get subjects from teacher's classes
    subjects = Subject.query.join(Class).filter(Class.teacher_id == current_user.id).all()
    return render_template('teacher/subjects.html', subjects=subjects)

@app.route('/teacher/create-subject', methods=['GET', 'POST'])
@login_required
def create_subject():
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form['name']
        class_id = request.form['class_id']
        description = request.form.get('description', '')
        
        # Check if subject already exists in this class
        existing_subject = Subject.query.filter_by(name=name, class_id=class_id).first()
        if existing_subject:
            flash('Subject already exists in this class', 'error')
            return redirect(url_for('create_subject'))
        
        subject = Subject(
            name=name,
            class_id=class_id,
            description=description,
            teacher_id=current_user.id
        )
        db.session.add(subject)
        db.session.commit()
        flash('Subject created successfully!', 'success')
        return redirect(url_for('manage_subjects'))
    
    # Get teacher's classes
    classes = Class.query.filter_by(teacher_id=current_user.id).all()
    return render_template('teacher/create_subject.html', classes=classes)

# Create assignment route
@app.route('/teacher/create-assignment', methods=['GET', 'POST'])
@login_required
def teacher_create_assignment():
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        print("DEBUG: Assignment form submitted!")
        print(f"DEBUG: Form data: {request.form}")
        
        title = request.form['title']
        description = request.form.get('description', '')
        subject_id = request.form['subject_id']
        due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d').date()
        
        print(f"DEBUG: Creating assignment - Title: {title}, Subject ID: {subject_id}, Teacher ID: {current_user.id}")
        
        assignment = Assignment(
            title=title,
            description=description,
            subject_id=subject_id,
            due_date=due_date,
            teacher_id=current_user.id
        )
        db.session.add(assignment)
        db.session.commit()
        print(f"DEBUG: Assignment created with ID: {assignment.id}")
        
        # Create notification for admin
        admin_user = User.query.filter_by(role='admin').first()
        if admin_user:
            create_notification(
                user_id=admin_user.id,
                notification_type='assignment_created',
                title='New Assignment Created',
                content=f'Teacher {current_user.first_name} {current_user.last_name} created a new assignment: "{title}"'
            )
        
        flash('Assignment created successfully!', 'success')
        return redirect(url_for('teacher_dashboard'))
    
    # Get subjects for current teacher's classes
    subjects = Subject.query.join(Class).filter(Class.teacher_id == current_user.id).all()
    return render_template('teacher/create_assignment.html', subjects=subjects)

# Assignment distribution and marking routes
@app.route('/teacher/assign-assignment/<int:assignment_id>')
@login_required
def assign_assignment(assignment_id):
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.teacher_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('teacher_dashboard'))
    
    # Get students from the assignment's subject class
    students = Student.query.filter_by(class_id=assignment.subject.class_id).all()
    
    # Get existing assignment records
    existing_records = AssignmentRecord.query.filter_by(assignment_id=assignment_id).all()
    assigned_student_ids = [record.student_id for record in existing_records]
    
    return render_template('teacher/assign_assignment.html', 
                         assignment=assignment, 
                         students=students, 
                         assigned_student_ids=assigned_student_ids)

@app.route('/teacher/assign-assignment/<int:assignment_id>', methods=['POST'])
@login_required
def process_assignment_assignment(assignment_id):
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.teacher_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('teacher_dashboard'))
    
    selected_students = request.form.getlist('student_ids')
    
    # Create assignment records for selected students
    for student_id in selected_students:
        # Check if record already exists
        existing_record = AssignmentRecord.query.filter_by(
            student_id=student_id, 
            assignment_id=assignment_id
        ).first()
        
        if not existing_record:
            assignment_record = AssignmentRecord(
                student_id=student_id,
                assignment_id=assignment_id,
                completed=False
            )
            db.session.add(assignment_record)
    
    db.session.commit()
    flash(f'Assignment assigned to {len(selected_students)} students successfully!', 'success')
    return redirect(url_for('view_assignment', assignment_id=assignment_id))

@app.route('/teacher/mark-assignment/<int:assignment_id>')
@login_required
def mark_assignment_page(assignment_id):
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.teacher_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('teacher_dashboard'))
    
    # Get assignment records for this assignment
    assignment_records = AssignmentRecord.query.filter_by(assignment_id=assignment_id).all()
    
    return render_template('teacher/mark_assignment.html', 
                         assignment=assignment, 
                         assignment_records=assignment_records)

@app.route('/teacher/mark-assignment/<int:assignment_id>', methods=['POST'])
@login_required
def process_mark_assignment(assignment_id):
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.teacher_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('teacher_dashboard'))
    
    # Process marking for each student
    for key, value in request.form.items():
        if key.startswith('completed_'):
            student_id = int(key.split('_')[1])
            completed = value == 'yes'
            
            # Get or create assignment record
            assignment_record = AssignmentRecord.query.filter_by(
                student_id=student_id,
                assignment_id=assignment_id
            ).first()
            
            if assignment_record:
                assignment_record.completed = completed
                if completed:
                    assignment_record.submitted_date = datetime.utcnow().date()
                else:
                    assignment_record.submitted_date = None
                
                # Update grade and feedback if provided
                grade_key = f'grade_{student_id}'
                feedback_key = f'feedback_{student_id}'
                
                if grade_key in request.form:
                    assignment_record.grade = request.form[grade_key]
                if feedback_key in request.form:
                    assignment_record.feedback = request.form[feedback_key]
    
    db.session.commit()
    flash('Assignment marking updated successfully!', 'success')
    return redirect(url_for('view_assignment', assignment_id=assignment_id))

# Admin password reset functionality
@app.route('/admin/reset-password/<int:user_id>')
@login_required
def admin_reset_password(user_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    return render_template('admin/reset_password.html', user=user)

@app.route('/admin/reset-password/<int:user_id>', methods=['POST'])
@login_required
def process_admin_reset_password(user_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']
    
    if new_password != confirm_password:
        flash('Passwords do not match', 'error')
        return redirect(url_for('admin_reset_password', user_id=user_id))
    
    if len(new_password) < 6:
        flash('Password must be at least 6 characters long', 'error')
        return redirect(url_for('admin_reset_password', user_id=user_id))
    
    # Reset password
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    
    flash(f'Password reset successfully for {user.first_name} {user.last_name}', 'success')
    return redirect(url_for('manage_teachers'))

# Additional missing routes
@app.route('/teacher/class/<int:class_id>')
@login_required
def view_class(class_id):
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    class_obj = Class.query.get_or_404(class_id)
    if class_obj.teacher_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    return render_template('teacher/view_class.html', class_obj=class_obj)

@app.route('/teacher/assignment/<int:assignment_id>')
@login_required
def view_assignment(assignment_id):
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.teacher_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    return render_template('teacher/view_assignment.html', assignment=assignment)

@app.route('/teacher/assignment/<int:assignment_id>/edit')
@login_required
def edit_assignment(assignment_id):
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.teacher_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    return render_template('teacher/edit_assignment.html', assignment=assignment)

# Edit class route
@app.route('/teacher/class/<int:class_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_class(class_id):
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    class_obj = Class.query.get_or_404(class_id)
    if class_obj.teacher_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        class_obj.name = request.form['name']
        class_obj.grade_level = request.form['grade_level']
        db.session.commit()
        flash('Class updated successfully!', 'success')
        return redirect(url_for('view_class', class_id=class_id))
    
    return render_template('teacher/edit_class.html', class_obj=class_obj)

# Homework Record routes
@app.route('/teacher/homework-records')
@login_required
def teacher_homework_records():
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Get teacher's classes and homework records
    classes = Class.query.filter_by(teacher_id=current_user.id).all()
    homework_records = HomeworkRecord.query.filter_by(teacher_id=current_user.id).order_by(HomeworkRecord.created_at.desc()).all()
    
    return render_template('teacher/homework_records.html', classes=classes, homework_records=homework_records)

@app.route('/teacher/homework-record/create', methods=['GET', 'POST'])
@login_required
def create_homework_record():
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        week = request.form.get('week')
        description = request.form.get('description')
        class_id = request.form.get('class_id')
        
        if not week or not description or not class_id:
            flash('All fields are required', 'error')
            return redirect(url_for('create_homework_record'))
        
        # Verify the class belongs to the teacher
        class_obj = Class.query.filter_by(id=class_id, teacher_id=current_user.id).first()
        if not class_obj:
            flash('Invalid class selection', 'error')
            return redirect(url_for('create_homework_record'))
        
        homework_record = HomeworkRecord(
            week=week,
            description=description,
            class_id=class_id,
            teacher_id=current_user.id
        )
        
        try:
            db.session.add(homework_record)
            db.session.commit()
            
            # Create notification for admin
            admin_user = User.query.filter_by(role='admin').first()
            if admin_user:
                create_notification(
                    user_id=admin_user.id,
                    notification_type='homework_record_created',
                    title='New Homework Record Created',
                    content=f'Teacher {current_user.first_name} {current_user.last_name} created a homework record for Week {week} in {class_obj.name}'
                )
            
            flash('Homework record created successfully', 'success')
            return redirect(url_for('teacher_homework_records'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating homework record', 'error')
    
    # Get teacher's classes for the form
    classes = Class.query.filter_by(teacher_id=current_user.id).all()
    return render_template('teacher/create_homework_record.html', classes=classes)

@app.route('/admin/homework-records')
@login_required
def admin_homework_records():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Get filter parameters
    class_filter = request.args.get('class_filter', '')
    week_filter = request.args.get('week_filter', '')
    teacher_filter = request.args.get('teacher_filter', '')
    
    # Get all classes for filter dropdown
    all_classes = Class.query.all()
    
    # Build query
    query = HomeworkRecord.query
    
    if class_filter:
        query = query.filter(HomeworkRecord.class_id == class_filter)
    if week_filter:
        query = query.filter(HomeworkRecord.week == week_filter)
    if teacher_filter:
        query = query.filter(HomeworkRecord.teacher_id == teacher_filter)
    
    # Get filtered homework records
    homework_records = query.order_by(HomeworkRecord.created_at.desc()).all()
    
    return render_template('admin/homework_records.html', 
                         homework_records=homework_records,
                         all_classes=all_classes,
                         class_filter=class_filter,
                         week_filter=week_filter,
                         teacher_filter=teacher_filter)

@app.route('/admin/homework-record/<int:record_id>')
@login_required
def admin_view_homework_record(record_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    record = HomeworkRecord.query.get_or_404(record_id)
    comments = HomeworkComment.query.filter_by(homework_record_id=record_id).order_by(HomeworkComment.created_at.desc()).all()
    
    return render_template('admin/homework_record_detail.html', record=record, comments=comments)

@app.route('/admin/homework-record/<int:record_id>/comment', methods=['POST'])
@login_required
def admin_comment_homework_record(record_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    record = HomeworkRecord.query.get_or_404(record_id)
    comment_text = request.form.get('comment')
    
    if not comment_text:
        flash('Comment cannot be empty', 'error')
        return redirect(url_for('admin_view_homework_record', record_id=record_id))
    
    comment = HomeworkComment(
        homework_record_id=record_id,
        admin_id=current_user.id,
        comment=comment_text
    )
    
    try:
        db.session.add(comment)
        db.session.commit()
        flash('Comment added successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error adding comment', 'error')
    
    return redirect(url_for('admin_view_homework_record', record_id=record_id))

# Teacher homework record view and edit routes
@app.route('/teacher/homework-record/<int:record_id>')
@login_required
def teacher_view_homework_record(record_id):
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    record = HomeworkRecord.query.get_or_404(record_id)
    if record.teacher_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    return render_template('teacher/homework_record_detail.html', record=record)

@app.route('/teacher/homework-record/<int:record_id>/edit', methods=['GET', 'POST'])
@login_required
def teacher_edit_homework_record(record_id):
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    record = HomeworkRecord.query.get_or_404(record_id)
    if record.teacher_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        record.week = request.form.get('week')
        record.description = request.form.get('description')
        record.class_id = request.form.get('class_id')
        
        # Verify the class belongs to the teacher
        class_obj = Class.query.filter_by(id=record.class_id, teacher_id=current_user.id).first()
        if not class_obj:
            flash('Invalid class selection', 'error')
            return redirect(url_for('teacher_edit_homework_record', record_id=record_id))
        
        try:
            db.session.commit()
            flash('Homework record updated successfully', 'success')
            return redirect(url_for('teacher_homework_records'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating homework record', 'error')
    
    # Get teacher's classes for the form
    classes = Class.query.filter_by(teacher_id=current_user.id).all()
    return render_template('teacher/edit_homework_record.html', record=record, classes=classes)

@app.route('/admin/send-message', methods=['GET', 'POST'])
@login_required
def admin_send_message():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        subject = request.form.get('subject')
        content = request.form.get('content')
        recipient_type = request.form.get('recipient_type')  # 'all' or 'specific'
        teacher_id = request.form.get('teacher_id')
        
        if not subject or not content:
            flash('Subject and content are required', 'error')
            return redirect(url_for('admin_send_message'))
        
        try:
            if recipient_type == 'all':
                # Send to all teachers
                teachers = User.query.filter_by(role='teacher').all()
                for teacher in teachers:
                    message = Message(
                        sender_id=current_user.id,
                        recipient_id=teacher.id,
                        subject=subject,
                        content=content
                    )
                    db.session.add(message)
                flash(f'Message sent to all {len(teachers)} teachers', 'success')
            else:
                # Send to specific teacher
                if not teacher_id:
                    flash('Please select a teacher', 'error')
                    return redirect(url_for('admin_send_message'))
                
                message = Message(
                    sender_id=current_user.id,
                    recipient_id=teacher_id,
                    subject=subject,
                    content=content
                )
                db.session.add(message)
                flash('Message sent successfully', 'success')
            
            db.session.commit()
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Error sending message', 'error')
    
    # Get all teachers for the form
    teachers = User.query.filter_by(role='teacher').all()
    return render_template('admin/send_message.html', teachers=teachers)

@app.route('/teacher/messages')
@login_required
def teacher_messages():
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    messages = Message.query.filter_by(recipient_id=current_user.id).order_by(Message.created_at.desc()).all()
    return render_template('teacher/messages.html', messages=messages)

@app.route('/teacher/message/<int:message_id>/read', methods=['POST'])
@login_required
def mark_message_read(message_id):
    if current_user.role != 'teacher':
        return jsonify({'error': 'Access denied'}), 403
    
    message = Message.query.filter_by(id=message_id, recipient_id=current_user.id).first()
    if message:
        message.is_read = True
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'error': 'Message not found'}), 404

@app.route('/api/teacher/notifications')
@login_required
def teacher_notifications():
    if current_user.role != 'teacher':
        return jsonify({'error': 'Access denied'}), 403
    
    unread_messages = Message.query.filter_by(recipient_id=current_user.id, is_read=False).count()
    recent_homework_comments = HomeworkComment.query.join(HomeworkRecord).filter(
        HomeworkRecord.teacher_id == current_user.id
    ).order_by(HomeworkComment.created_at.desc()).limit(5).all()
    
    return jsonify({
        'unread_messages': unread_messages,
        'recent_comments': [{
            'id': comment.id,
            'homework_record_id': comment.homework_record_id,
            'week': comment.homework_record.week,
            'comment': comment.comment,
            'created_at': comment.created_at.isoformat(),
            'admin_name': comment.admin.first_name + ' ' + comment.admin.last_name
        } for comment in recent_homework_comments]
    })

@app.route('/admin/teacher-submissions')
@login_required
def admin_teacher_submissions():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Get filter parameters
    week_filter = request.args.get('week_filter', '')
    
    # Get all teachers
    teachers = User.query.filter_by(role='teacher').all()
    
    # Determine which week to show
    if week_filter:
        current_week = week_filter
    else:
        # Get current week (you can modify this logic based on your needs)
        from datetime import datetime, timedelta
        current_date = datetime.now()
        week_number = current_date.isocalendar()[1]
        current_week = f"Week {week_number}"
    
    # Get homework records for selected week
    try:
        current_week_records = HomeworkRecord.query.filter_by(week=current_week).all()
        submitted_teacher_ids = [record.teacher_id for record in current_week_records]
    except Exception as e:
        print(f"Error fetching homework records: {e}")
        current_week_records = []
        submitted_teacher_ids = []
    
    # Categorize teachers
    submitted_teachers = []
    not_submitted_teachers = []
    
    for teacher in teachers:
        if teacher.id in submitted_teacher_ids:
            # Get their submission details
            record = next((r for r in current_week_records if r.teacher_id == teacher.id), None)
            submitted_teachers.append({
                'teacher': teacher,
                'record': record,
                'submission_count': HomeworkRecord.query.filter_by(teacher_id=teacher.id).count()
            })
        else:
            not_submitted_teachers.append({
                'teacher': teacher,
                'submission_count': HomeworkRecord.query.filter_by(teacher_id=teacher.id).count()
            })
    
    return render_template('admin/teacher_submissions.html', 
                         submitted_teachers=submitted_teachers,
                         not_submitted_teachers=not_submitted_teachers,
                         current_week=current_week,
                         week_filter=week_filter)

@app.route('/teacher/message/<int:message_id>/reply', methods=['GET', 'POST'])
@login_required
def teacher_reply_message(message_id):
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    original_message = Message.query.filter_by(id=message_id, recipient_id=current_user.id).first()
    if not original_message:
        flash('Message not found', 'error')
        return redirect(url_for('teacher_messages'))
    
    if request.method == 'POST':
        reply_content = request.form.get('content')
        
        if not reply_content:
            flash('Reply content cannot be empty', 'error')
            return redirect(url_for('teacher_reply_message', message_id=message_id))
        
        # Create reply message
        reply = Message(
            sender_id=current_user.id,
            recipient_id=original_message.sender_id,
            subject=f"Re: {original_message.subject}",
            content=reply_content,
            parent_message_id=message_id
        )
        
        try:
            db.session.add(reply)
            
            # Create notification for admin about the reply
            admin = User.query.filter_by(role='admin').first()
            if admin:
                notification = Notification(
                    user_id=admin.id,
                    message_id=reply.id,
                    type='message_reply',
                    title=f'New Reply from {current_user.first_name} {current_user.last_name}',
                    content=f'Re: {original_message.subject}'
                )
                db.session.add(notification)
            
            db.session.commit()
            flash('Reply sent successfully', 'success')
            return redirect(url_for('teacher_messages'))
        except Exception as e:
            db.session.rollback()
            flash('Error sending reply', 'error')
    
    return render_template('teacher/reply_message.html', message=original_message)

# Admin notification routes
@app.route('/admin/notifications')
@login_required
def admin_notifications():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Get unread notifications count
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    
    # Get all notifications for admin
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    
    return render_template('admin/notifications.html', notifications=notifications, unread_count=unread_count)

@app.route('/admin/notification/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    notification = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first()
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404
    
    try:
        notification.is_read = True
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to mark notification as read'}), 500

@app.route('/admin/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to mark all notifications as read'}), 500

@app.route('/admin/notifications/count')
@login_required
def admin_notification_count():
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        return jsonify({'count': unread_count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/message/<int:message_id>')
@login_required
def admin_view_message(message_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    message = Message.query.get_or_404(message_id)
    replies = Message.query.filter_by(parent_message_id=message_id).order_by(Message.created_at.asc()).all()
    
    return render_template('admin/message_detail.html', message=message, replies=replies)

# Profile route
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

# Lesson Plans and Notes Routes
@app.route('/teacher/lessons')
@login_required
def teacher_lessons():
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Get filter parameters
    week_filter = request.args.get('week_filter', '')
    term_filter = request.args.get('term_filter', '')
    status_filter = request.args.get('status_filter', '')
    
    # Build query
    query = Lesson.query.filter_by(teacher_id=current_user.id)
    
    if week_filter:
        query = query.filter(Lesson.week == week_filter)
    if term_filter:
        query = query.filter(Lesson.term == term_filter)
    if status_filter:
        query = query.filter(Lesson.status == status_filter)
    
    lessons = query.order_by(Lesson.created_at.desc()).all()
    
    # Get unique terms and weeks for filters
    all_lessons = Lesson.query.filter_by(teacher_id=current_user.id).all()
    terms = sorted(list(set([lesson.term for lesson in all_lessons if lesson.term])))
    weeks = sorted(list(set([lesson.week for lesson in all_lessons if lesson.week])))
    
    return render_template('teacher/lessons.html', 
                         lessons=lessons, 
                         terms=terms, 
                         weeks=weeks,
                         week_filter=week_filter,
                         term_filter=term_filter,
                         status_filter=status_filter)

@app.route('/teacher/lessons/create', methods=['GET', 'POST'])
@login_required
def create_lesson():
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        subject_id = request.form.get('subject_id')
        week = request.form.get('week')
        term = request.form.get('term')
        session = request.form.get('session')
        
        # Lesson Plan fields
        objectives = request.form.get('objectives')
        content = request.form.get('content')
        activities = request.form.get('activities')
        resources = request.form.get('resources')
        assessment = request.form.get('assessment')
        
        # Lesson Note fields
        lesson_notes = request.form.get('lesson_notes')
        student_attendance = request.form.get('student_attendance')
        student_performance = request.form.get('student_performance')
        challenges = request.form.get('challenges')
        next_steps = request.form.get('next_steps')
        
        # Status and dates
        status = request.form.get('status', 'planned')
        completion_percentage = int(request.form.get('completion_percentage', 0))
        planned_date_str = request.form.get('planned_date')
        taught_date_str = request.form.get('taught_date')
        
        if not title or not subject_id or not week or not term or not session:
            flash('Please fill in all required fields', 'error')
            return redirect(url_for('create_lesson'))
        
        # Verify the subject belongs to the teacher
        subject = Subject.query.filter_by(id=subject_id, teacher_id=current_user.id).first()
        if not subject:
            flash('Invalid subject selection', 'error')
            return redirect(url_for('create_lesson'))
        
        # Parse dates
        planned_date = None
        taught_date = None
        if planned_date_str:
            planned_date = datetime.strptime(planned_date_str, '%Y-%m-%d').date()
        if taught_date_str:
            taught_date = datetime.strptime(taught_date_str, '%Y-%m-%d').date()
        
        # Create lesson
        lesson = Lesson(
            title=title,
            subject_id=subject_id,
            teacher_id=current_user.id,
            week=week,
            term=term,
            session=session,
            objectives=objectives,
            content=content,
            activities=activities,
            resources=resources,
            assessment=assessment,
            lesson_notes=lesson_notes,
            student_attendance=student_attendance,
            student_performance=student_performance,
            challenges=challenges,
            next_steps=next_steps,
            status=status,
            completion_percentage=completion_percentage,
            planned_date=planned_date,
            taught_date=taught_date
        )
        
        try:
            db.session.add(lesson)
            db.session.flush()  # Get the lesson ID
            
            # Handle file uploads
            if 'attachments' in request.files:
                files = request.files.getlist('attachments')
                for file in files:
                    if file and file.filename:
                        if allowed_lesson_file(file.filename):
                            filename = secure_filename(f"lesson_{lesson.id}_{file.filename}")
                            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'lessons', filename)
                            os.makedirs(os.path.dirname(filepath), exist_ok=True)
                            file.save(filepath)
                            
                            # Determine attachment type based on form data
                            attachment_type = request.form.get('attachment_type', 'resource')
                            
                            attachment = LessonAttachment(
                                lesson_id=lesson.id,
                                filename=filename,
                                original_filename=file.filename,
                                file_path=f"uploads/lessons/{filename}",
                                file_type=file.filename.rsplit('.', 1)[1].lower(),
                                file_size=os.path.getsize(filepath),
                                attachment_type=attachment_type
                            )
                            db.session.add(attachment)
            
            db.session.commit()
            
            # Create notification for admin
            admin_user = User.query.filter_by(role='admin').first()
            if admin_user:
                lesson_type = "Lesson Plan" if status == "planned" else "Lesson Note"
                create_notification(
                    user_id=admin_user.id,
                    notification_type='lesson_created',
                    title=f'New {lesson_type} Created',
                    content=f'Teacher {current_user.first_name} {current_user.last_name} created a {lesson_type.lower()}: "{title}" for Week {week}, Term {term}'
                )
            
            flash('Lesson created successfully!', 'success')
            return redirect(url_for('teacher_lessons'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating lesson', 'error')
            print(f"Error creating lesson: {e}")
    
    # Get teacher's subjects for the form
    subjects = Subject.query.join(Class).filter(Class.teacher_id == current_user.id).all()
    
    # Get current academic session
    current_year = datetime.now().year
    next_year = current_year + 1
    current_session = f"{current_year}/{next_year}"
    
    return render_template('teacher/create_lesson.html', 
                         subjects=subjects, 
                         current_session=current_session)

@app.route('/teacher/lessons/<int:lesson_id>')
@login_required
def view_lesson(lesson_id):
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    lesson = Lesson.query.get_or_404(lesson_id)
    
    # Check if teacher owns this lesson
    if lesson.teacher_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('teacher_lessons'))
    
    return render_template('teacher/view_lesson.html', lesson=lesson)

@app.route('/teacher/lessons/<int:lesson_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_lesson(lesson_id):
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    lesson = Lesson.query.get_or_404(lesson_id)
    
    # Check if teacher owns this lesson
    if lesson.teacher_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('teacher_lessons'))
    
    if request.method == 'POST':
        lesson.title = request.form.get('title')
        lesson.subject_id = request.form.get('subject_id')
        lesson.week = request.form.get('week')
        lesson.term = request.form.get('term')
        lesson.session = request.form.get('session')
        
        # Lesson Plan fields
        lesson.objectives = request.form.get('objectives')
        lesson.content = request.form.get('content')
        lesson.activities = request.form.get('activities')
        lesson.resources = request.form.get('resources')
        lesson.assessment = request.form.get('assessment')
        
        # Lesson Note fields
        lesson.lesson_notes = request.form.get('lesson_notes')
        lesson.student_attendance = request.form.get('student_attendance')
        lesson.student_performance = request.form.get('student_performance')
        lesson.challenges = request.form.get('challenges')
        lesson.next_steps = request.form.get('next_steps')
        
        # Status and dates
        lesson.status = request.form.get('status', 'planned')
        lesson.completion_percentage = int(request.form.get('completion_percentage', 0))
        
        planned_date_str = request.form.get('planned_date')
        taught_date_str = request.form.get('taught_date')
        
        if planned_date_str:
            lesson.planned_date = datetime.strptime(planned_date_str, '%Y-%m-%d').date()
        else:
            lesson.planned_date = None
            
        if taught_date_str:
            lesson.taught_date = datetime.strptime(taught_date_str, '%Y-%m-%d').date()
        else:
            lesson.taught_date = None
        
        try:
            # Check if status changed to notify admin
            old_status = lesson.status
            new_status = request.form.get('status', 'planned')
            
            db.session.commit()
            
            # Create notification for admin if lesson status changed
            if old_status != new_status:
                admin_user = User.query.filter_by(role='admin').first()
                if admin_user:
                    lesson_type = "Lesson Plan" if new_status == "planned" else "Lesson Note"
                    create_notification(
                        user_id=admin_user.id,
                        notification_type='lesson_updated',
                        title=f'Lesson Status Updated',
                        content=f'Teacher {current_user.first_name} {current_user.last_name} updated lesson "{lesson.title}" status from {old_status} to {new_status}'
                    )
            
            flash('Lesson updated successfully!', 'success')
            return redirect(url_for('view_lesson', lesson_id=lesson.id))
            
        except Exception as e:
            db.session.rollback()
            flash('Error updating lesson. Please try again.', 'error')
            print(f"Error updating lesson: {e}")
            return redirect(url_for('edit_lesson', lesson_id=lesson.id))
    
    # Get subjects for the dropdown
    subjects = Subject.query.join(Class).filter(Class.teacher_id == current_user.id).all()
    
    return render_template('teacher/edit_lesson.html', lesson=lesson, subjects=subjects)

@app.route('/teacher/lessons/<int:lesson_id>/delete', methods=['POST'])
@login_required
def delete_lesson(lesson_id):
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    lesson = Lesson.query.get_or_404(lesson_id)
    
    # Check if teacher owns this lesson
    if lesson.teacher_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('teacher_lessons'))
    
    try:
        # Delete associated attachments
        for attachment in lesson.attachments:
            if os.path.exists(attachment.file_path):
                os.remove(attachment.file_path)
        
        db.session.delete(lesson)
        db.session.commit()
        flash('Lesson deleted successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error deleting lesson. Please try again.', 'error')
        print(f"Error deleting lesson: {e}")
    
    return redirect(url_for('teacher_lessons'))

def allowed_lesson_file(filename):
    """Check if file extension is allowed for lesson plans/notes"""
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'rtf'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_setting(key, default=None):
    """Get a system setting value"""
    setting = SystemSetting.query.filter_by(key=key).first()
    return setting.value if setting else default

def set_setting(key, value):
    """Set a system setting value"""
    setting = SystemSetting.query.filter_by(key=key).first()
    if setting:
        setting.value = value
    else:
        setting = SystemSetting(key=key, value=value)
        db.session.add(setting)
    db.session.commit()
    return setting

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Start auto backup scheduler in background thread
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        # Schedule initial auto backup settings
        schedule_auto_backup()
        
        # Create admin user if it doesn't exist
        if not User.query.filter_by(username='admin').first():
            admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
            admin = User(
                username='admin',
                email='admin@school.com',
                password_hash=generate_password_hash(admin_password),
                role='admin',
                first_name='Admin',
                last_name='User'
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: username=admin, password=admin123")
        
        # Create teacher user if it doesn't exist
        if not User.query.filter_by(username='teacher1').first():
            teacher_password = os.getenv('TEACHER_PASSWORD', 'teacher123')
            teacher = User(
                username='teacher1',
                email='teacher1@school.com',
                password_hash=generate_password_hash(teacher_password),
                role='teacher',
                first_name='John',
                last_name='Teacher'
            )
            db.session.add(teacher)
            db.session.commit()
            print("Teacher user created: username=teacher1, password=teacher123")
        
        # Create parent user if it doesn't exist
        if not User.query.filter_by(username='parent1').first():
            parent_password = os.getenv('PARENT_PASSWORD', 'parent123')
            parent = User(
                username='parent1',
                email='parent1@school.com',
                password_hash=generate_password_hash(parent_password),
                role='parent',
                first_name='Jane',
                last_name='Parent'
            )
            db.session.add(parent)
            db.session.flush()
            print("Parent user created: username=parent1, password=parent123")
        
        # Create sample class if it doesn't exist
        if not Class.query.first():
            # Get the teacher we just created
            teacher = User.query.filter_by(role='teacher').first()
            sample_class = Class(
                name='Basic 5A',
                grade_level='5',
                teacher_id=teacher.id
            )
            db.session.add(sample_class)
            db.session.flush()
            print("Sample class created: Basic 5A")
            
            # Create sample subjects
            math_subject = Subject(
                name='Mathematics',
                class_id=sample_class.id,
                teacher_id=teacher.id
            )
            english_subject = Subject(
                name='English Language',
                class_id=sample_class.id,
                teacher_id=teacher.id
            )
            db.session.add(math_subject)
            db.session.add(english_subject)
            db.session.flush()
            print("Sample subjects created")
            
            # Create sample students
            student1 = Student(
                first_name='Alice',
                last_name='Johnson',
                student_id=Student.generate_student_id(),
                class_id=sample_class.id,
                parent_id=parent.id
            )
            student2 = Student(
                first_name='Bob',
                last_name='Smith',
                student_id=Student.generate_student_id(),
                class_id=sample_class.id
            )
            db.session.add(student1)
            db.session.add(student2)
            db.session.commit()
            print("Sample students created")
    
    app.run(debug=True)
