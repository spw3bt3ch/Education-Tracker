#!/usr/bin/env python3
"""
Production Deployment Script for Student Assignment Tracking App with Aiven
Configures the application for production deployment with Aiven cloud database
"""

import os
import sys
from dotenv import load_dotenv

def check_production_requirements():
    """Check if all production requirements are met"""
    print("🔍 Checking production requirements...")
    
    issues = []
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        issues.append("❌ .env file not found")
    else:
        load_dotenv()
        
        # Check critical environment variables
        required_vars = ['DATABASE_URL', 'SECRET_KEY']
        for var in required_vars:
            if not os.getenv(var):
                issues.append(f"❌ {var} not set in .env file")
        
        # Check if DATABASE_URL is not SQLite
        database_url = os.getenv('DATABASE_URL', '')
        if database_url.startswith('sqlite'):
            issues.append("❌ DATABASE_URL should point to Aiven database, not SQLite")
    
    # Check if backup exists
    if not os.path.exists('backups'):
        issues.append("⚠️  No backup directory found - consider creating a backup first")
    
    if issues:
        print("Issues found:")
        for issue in issues:
            print(f"  {issue}")
        return False
    
    print("✅ All production requirements met!")
    return True

def create_production_config():
    """Create production configuration files"""
    print("🔧 Creating production configuration...")
    
    # Create .env.production template
    production_env = """# Production Environment Configuration
# Copy this to .env and update with your actual values

# Aiven Database Configuration
DATABASE_URL=postgresql://username:password@hostname:port/database_name
# or for MySQL:
# DATABASE_URL=mysql://username:password@hostname:port/database_name

# Flask Configuration
SECRET_KEY=your-super-secret-production-key-here
FLASK_ENV=production
FLASK_DEBUG=False

# Optional: Database connection pooling
SQLALCHEMY_ENGINE_OPTIONS={"pool_size": 10, "pool_recycle": 3600, "pool_pre_ping": True}

# Optional: Logging configuration
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Optional: Security headers
FORCE_HTTPS=True
"""
    
    with open('.env.production', 'w') as f:
        f.write(production_env)
    
    print("✅ Created .env.production template")
    
    # Create gunicorn configuration
    gunicorn_config = """# Gunicorn configuration for production
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True

# Logging
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"

# Process naming
proc_name = "edutrack-app"
"""
    
    with open('gunicorn.conf.py', 'w') as f:
        f.write(gunicorn_config)
    
    print("✅ Created gunicorn.conf.py")
    
    # Create systemd service file
    systemd_service = """[Unit]
Description=Student Assignment Tracking App
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/app
Environment=PATH=/path/to/your/app/venv/bin
ExecStart=/path/to/your/app/venv/bin/gunicorn --config gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
"""
    
    with open('edutrack.service', 'w') as f:
        f.write(systemd_service)
    
    print("✅ Created edutrack.service (systemd)")
    
    # Create nginx configuration
    nginx_config = """server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL configuration (update paths to your certificates)
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # Static files
    location /static {
        alias /path/to/your/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
"""
    
    with open('nginx.conf', 'w') as f:
        f.write(nginx_config)
    
    print("✅ Created nginx.conf")

def create_docker_files():
    """Create Docker configuration files"""
    print("🐳 Creating Docker configuration...")
    
    # Create Dockerfile
    dockerfile = """FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/ || exit 1

# Run application
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]
"""
    
    with open('Dockerfile', 'w') as f:
        f.write(dockerfile)
    
    print("✅ Created Dockerfile")
    
    # Create docker-compose.yml
    docker_compose = """version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
      - FLASK_ENV=production
    volumes:
      - ./static/uploads:/app/static/uploads
      - ./logs:/app/logs
    restart: unless-stopped
    depends_on:
      - redis
    
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data

volumes:
  redis_data:
"""
    
    with open('docker-compose.yml', 'w') as f:
        f.write(docker_compose)
    
    print("✅ Created docker-compose.yml")

def create_monitoring_config():
    """Create monitoring and logging configuration"""
    print("📊 Creating monitoring configuration...")
    
    # Create logging configuration
    logging_config = """import logging
import logging.handlers
import os

def setup_logging():
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.handlers.RotatingFileHandler(
                'logs/app.log',
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )
    
    # Set specific loggers
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
"""
    
    with open('logging_config.py', 'w') as f:
        f.write(logging_config)
    
    print("✅ Created logging_config.py")
    
    # Create health check script
    health_check = """#!/usr/bin/env python3
import requests
import sys

def check_health():
    try:
        response = requests.get('http://localhost:8000/', timeout=10)
        if response.status_code == 200:
            print("✅ Application is healthy")
            return 0
        else:
            print(f"❌ Application returned status {response.status_code}")
            return 1
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(check_health())
"""
    
    with open('health_check.py', 'w') as f:
        f.write(health_check)
    
    # Make health check executable
    os.chmod('health_check.py', 0o755)
    
    print("✅ Created health_check.py")

def main():
    """Main deployment function"""
    print("🚀 Student Assignment Tracking App - Production Deployment Setup")
    print("=" * 70)
    
    # Check requirements
    if not check_production_requirements():
        print("\n💥 Cannot proceed with deployment setup.")
        print("Please fix the issues above and run again.")
        sys.exit(1)
    
    print("\n🔧 Setting up production configuration...")
    
    # Create configuration files
    create_production_config()
    create_docker_files()
    create_monitoring_config()
    
    print("\n✅ Production deployment setup completed!")
    print("\n📋 Next steps:")
    print("1. Update .env.production with your actual values")
    print("2. Copy .env.production to .env")
    print("3. Update nginx.conf with your domain and SSL certificates")
    print("4. Update edutrack.service with correct paths")
    print("5. Test your application: python app.py")
    print("6. Deploy using your preferred method (Docker, systemd, etc.)")
    print("\n📚 See AIVEN_MIGRATION_GUIDE.md for detailed instructions")

if __name__ == '__main__':
    main()
