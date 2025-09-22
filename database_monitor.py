"""
Database Monitoring System for Super Admin
Provides comprehensive database space and usage monitoring
"""

import os
import sqlite3
import psutil
from datetime import datetime, timedelta
from flask import current_app
from sqlalchemy import text
import json

class DatabaseMonitor:
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        self.app = app
    
    def get_database_size(self):
        """Get current database size"""
        try:
            with current_app.app_context():
                if 'sqlite' in current_app.config['SQLALCHEMY_DATABASE_URI']:
                    # SQLite database
                    db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
                    if os.path.exists(db_path):
                        size_bytes = os.path.getsize(db_path)
                        return {
                            'size_bytes': size_bytes,
                            'size_mb': round(size_bytes / (1024 * 1024), 2),
                            'size_gb': round(size_bytes / (1024 * 1024 * 1024), 2)
                        }
                else:
                    # PostgreSQL/MySQL - get database size via SQL
                    from app import db
                    if 'postgresql' in current_app.config['SQLALCHEMY_DATABASE_URI']:
                        result = db.session.execute(text("""
                            SELECT pg_size_pretty(pg_database_size(current_database())) as size,
                                   pg_database_size(current_database()) as size_bytes
                        """)).fetchone()
                        size_bytes = result[1]
                    else:  # MySQL
                        result = db.session.execute(text("""
                            SELECT 
                                ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS size_mb,
                                SUM(data_length + index_length) AS size_bytes
                            FROM information_schema.tables 
                            WHERE table_schema = DATABASE()
                        """)).fetchone()
                        size_bytes = int(result[1])
                    
                    return {
                        'size_bytes': size_bytes,
                        'size_mb': round(size_bytes / (1024 * 1024), 2),
                        'size_gb': round(size_bytes / (1024 * 1024 * 1024), 2)
                    }
        except Exception as e:
            print(f"Error getting database size: {e}")
            return {'size_bytes': 0, 'size_mb': 0, 'size_gb': 0}
    
    def get_remaining_database_space(self, total_space_gb=None):
        """Calculate remaining database space assuming a total capacity"""
        try:
            with current_app.app_context():
                # Get total space from config or use default
                if total_space_gb is None:
                    total_space_gb = getattr(current_app.config, 'DATABASE_TOTAL_CAPACITY_GB', 1)
                
                used_size = self.get_database_size()
                total_space_bytes = total_space_gb * (1024 * 1024 * 1024)
                remaining_bytes = total_space_bytes - used_size['size_bytes']
                
                return {
                    'total_space_gb': total_space_gb,
                    'used_bytes': used_size['size_bytes'],
                    'remaining_bytes': max(0, remaining_bytes),
                    'remaining_kb': round(max(0, remaining_bytes) / 1024, 2),
                    'remaining_mb': round(max(0, remaining_bytes) / (1024 * 1024), 2),
                    'remaining_gb': round(max(0, remaining_bytes) / (1024 * 1024 * 1024), 2),
                    'usage_percentage': round((used_size['size_bytes'] / total_space_bytes) * 100, 2)
                }
        except Exception as e:
            print(f"Error getting remaining database space: {e}")
            # Return default values if there's an error
            return {
                'total_space_gb': 1,
                'used_bytes': 0,
                'remaining_bytes': 1024 * 1024 * 1024,  # 1GB
                'remaining_kb': 1024 * 1024,
                'remaining_mb': 1024,
                'remaining_gb': 1,
                'usage_percentage': 0
            }
    
    def get_table_sizes(self):
        """Get size of individual tables"""
        try:
            with current_app.app_context():
                from app import db
                
                if 'sqlite' in current_app.config['SQLALCHEMY_DATABASE_URI']:
                    # SQLite - get table info
                    db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    tables = []
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    for table_name in cursor.fetchall():
                        table_name = table_name[0]
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        row_count = cursor.fetchone()[0]
                        
                        # Estimate size (rough calculation)
                        cursor.execute(f"PRAGMA table_info({table_name})")
                        columns = cursor.fetchall()
                        estimated_size = row_count * len(columns) * 50  # Rough estimate
                        
                        tables.append({
                            'name': table_name,
                            'row_count': row_count,
                            'estimated_size_bytes': estimated_size,
                            'estimated_size_mb': round(estimated_size / (1024 * 1024), 2)
                        })
                    
                    conn.close()
                    return tables
                else:
                    # PostgreSQL/MySQL
                    if 'postgresql' in current_app.config['SQLALCHEMY_DATABASE_URI']:
                        query = text("""
                            SELECT 
                                schemaname,
                                tablename,
                                attname,
                                n_distinct,
                                correlation,
                                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                                pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
                            FROM pg_stats 
                            WHERE schemaname = 'public'
                            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                        """)
                    else:  # MySQL
                        query = text("""
                            SELECT 
                                table_name,
                                table_rows,
                                ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb,
                                (data_length + index_length) AS size_bytes
                            FROM information_schema.tables 
                            WHERE table_schema = DATABASE()
                            ORDER BY (data_length + index_length) DESC
                        """)
                    
                    result = db.session.execute(query).fetchall()
                    tables = []
                    for row in result:
                        tables.append({
                            'name': row[0],
                            'row_count': row[1] if len(row) > 1 else 0,
                            'size_bytes': row[-1] if len(row) > 2 else 0,
                            'size_mb': round(row[-1] / (1024 * 1024), 2) if len(row) > 2 else 0
                        })
                    return tables
        except Exception as e:
            print(f"Error getting table sizes: {e}")
            return []
    
    def get_school_storage_usage(self):
        """Get storage usage per school"""
        try:
            with current_app.app_context():
                from app import db, School, User, Assignment, Student, Class, HomeworkRecord, Lesson
                
                schools_data = []
                schools = School.query.all()
                
                for school in schools:
                    # Count records per school
                    users_count = User.query.filter_by(school_id=school.id).count()
                    students_count = Student.query.filter_by(school_id=school.id).count()
                    classes_count = Class.query.filter_by(school_id=school.id).count()
                    assignments_count = Assignment.query.filter_by(school_id=school.id).count()
                    homework_count = HomeworkRecord.query.filter_by(school_id=school.id).count()
                    lessons_count = Lesson.query.filter_by(school_id=school.id).count()
                    
                    # Estimate storage usage (realistic calculation for demo purposes)
                    estimated_storage = (
                        users_count * 50000 +  # ~50KB per user (includes profile data, settings, etc.)
                        students_count * 30000 +  # ~30KB per student (includes profile, grades, etc.)
                        classes_count * 20000 +  # ~20KB per class (includes class info, schedules)
                        assignments_count * 100000 +  # ~100KB per assignment (includes description, files, etc.)
                        homework_count * 50000 +  # ~50KB per homework record (includes submissions, feedback)
                        lessons_count * 80000  # ~80KB per lesson (includes content, materials)
                    )
                    
                    schools_data.append({
                        'school_id': school.id,
                        'school_name': school.name,
                        'school_code': school.code,
                        'users_count': users_count,
                        'students_count': students_count,
                        'classes_count': classes_count,
                        'assignments_count': assignments_count,
                        'homework_count': homework_count,
                        'lessons_count': lessons_count,
                        'total_records': users_count + students_count + classes_count + assignments_count + homework_count + lessons_count,
                        'estimated_storage_bytes': estimated_storage,
                        'estimated_storage_mb': round(estimated_storage / (1024 * 1024), 2),
                        'is_active': school.is_active
                    })
                
                return sorted(schools_data, key=lambda x: x['estimated_storage_bytes'], reverse=True)
        except Exception as e:
            print(f"Error getting school storage usage: {e}")
            return []
    
    def get_storage_growth_history(self, days=30):
        """Get storage growth history over time"""
        try:
            # This would require storing historical data
            # For now, return mock data structure
            return {
                'message': 'Storage growth tracking requires historical data storage',
                'suggestion': 'Implement daily storage snapshots'
            }
        except Exception as e:
            print(f"Error getting storage growth: {e}")
            return {}
    
    def get_system_resources(self):
        """Get system resource usage"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'available_memory_gb': round(psutil.virtual_memory().available / (1024**3), 2),
                'total_memory_gb': round(psutil.virtual_memory().total / (1024**3), 2)
            }
        except Exception as e:
            print(f"Error getting system resources: {e}")
            return {}
    
    def generate_storage_report(self):
        """Generate comprehensive storage report"""
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'database_size': self.get_database_size(),
                'table_sizes': self.get_table_sizes(),
                'school_usage': self.get_school_storage_usage(),
                'system_resources': self.get_system_resources(),
                'recommendations': self.get_storage_recommendations()
            }
            return report
        except Exception as e:
            print(f"Error generating storage report: {e}")
            return {}
    
    def get_storage_recommendations(self):
        """Get storage optimization recommendations"""
        try:
            recommendations = []
            db_size = self.get_database_size()
            school_usage = self.get_school_storage_usage()
            
            # Check database size
            if db_size['size_gb'] > 1:
                recommendations.append({
                    'type': 'warning',
                    'message': f"Database size is {db_size['size_gb']}GB. Consider archiving old data."
                })
            
            # Check for schools with high storage usage
            for school in school_usage[:3]:  # Top 3 schools by storage
                if school['estimated_storage_mb'] > 100:
                    recommendations.append({
                        'type': 'info',
                        'message': f"School '{school['school_name']}' uses {school['estimated_storage_mb']}MB. Monitor for growth."
                    })
            
            # Check system resources
            resources = self.get_system_resources()
            if resources.get('disk_usage', 0) > 80:
                recommendations.append({
                    'type': 'critical',
                    'message': f"Disk usage is {resources['disk_usage']}%. Consider cleanup or expansion."
                })
            
            return recommendations
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return []

# Initialize the monitor
db_monitor = DatabaseMonitor()
