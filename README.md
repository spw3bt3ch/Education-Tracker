# SMIED - Student Management Information Education Database

A comprehensive Flask-based web application for tracking student assignments, managing classes, and facilitating communication between teachers, administrators, and parents.

## Features

### 🎯 Core Functionality
- **Multi-role Authentication**: Admin, Teacher, and Parent portals
- **Student Management**: Add, edit, and track student information
- **Assignment Tracking**: Create, manage, and monitor assignments
- **Progress Monitoring**: Real-time tracking of student progress
- **Comment System**: Communication between teachers and administrators
- **Parent Portal**: Parents can view their child's progress

### 👨‍💼 Admin Features
- School-wide dashboard with statistics
- Teacher management
- Class oversight
- System reports and analytics
- Comment system for teacher feedback

### 👩‍🏫 Teacher Features
- Class management
- Student roster management
- Assignment creation and tracking
- Grade management
- Student progress monitoring

### 👨‍👩‍👧‍👦 Parent Features
- View child's assignment progress
- Track completion status
- Access to teacher comments
- Real-time notifications

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite (with SQLAlchemy ORM)
- **Frontend**: HTML5, CSS3, JavaScript
- **UI Framework**: Bootstrap 5
- **Authentication**: Flask-Login
- **Icons**: Font Awesome

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Step 1: Clone or Download
```bash
# If using git
git clone <repository-url>
cd Student-Assignment-Tracking-App

# Or download and extract the ZIP file
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Default Login Credentials

### Admin Account
- **Username**: admin
- **Password**: admin123
- **Role**: Head Teacher/Administrator

### Demo Accounts
You can create additional accounts through the admin panel or by modifying the database directly.

## Project Structure

```
Student Assignment Tracking App/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── auth/            # Authentication templates
│   ├── admin/           # Admin dashboard templates
│   ├── teacher/         # Teacher interface templates
│   └── parent/          # Parent portal templates
└── static/              # Static files
    ├── css/             # Stylesheets
    └── js/              # JavaScript files
```

## Database Schema

### Key Models
- **User**: Admin, Teacher, and Parent accounts
- **Student**: Student information and class assignments
- **Class**: Class information and teacher assignments
- **Subject**: Subjects within classes
- **Assignment**: Assignment details and metadata
- **AssignmentRecord**: Individual student assignment completion
- **Comment**: Communication system between users

## Usage Guide

### For Administrators
1. Login with admin credentials
2. Access the admin dashboard
3. Manage teachers and classes
4. Monitor school-wide progress
5. Generate reports

### For Teachers
1. Login with teacher credentials
2. Create and manage classes
3. Add students to classes
4. Create assignments
5. Track student progress
6. Provide feedback and grades

### For Parents
1. Login with parent credentials
2. View child's progress
3. Check assignment completion
4. Read teacher comments

## Customization

### Adding New Features
1. Modify `models.py` for database changes
2. Update `app.py` for new routes
3. Create templates in appropriate directories
4. Update navigation in `base.html`

### Styling
- Modify `static/css/style.css` for custom styles
- Update Bootstrap classes in templates
- Add custom JavaScript in `static/js/main.js`

## Security Considerations

- Change default admin password
- Use environment variables for sensitive data
- Implement proper input validation
- Add CSRF protection for forms
- Use HTTPS in production

## Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
1. Set up a production WSGI server (e.g., Gunicorn)
2. Configure a reverse proxy (e.g., Nginx)
3. Use a production database (PostgreSQL/MySQL)
4. Set up SSL certificates
5. Configure environment variables

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## Future Enhancements

- [ ] Email notifications
- [ ] Mobile app
- [ ] Advanced reporting
- [ ] Integration with school management systems
- [ ] Bulk data import/export
- [ ] Advanced analytics dashboard
- [ ] Multi-language support

---

**EduTrack** - Empowering education through technology
