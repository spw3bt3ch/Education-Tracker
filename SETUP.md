# SMIED Setup Instructions

## Environment Configuration

### 1. Create Environment File

Copy the configuration template to create your environment file:

```bash
cp config.env.template .env
```

### 2. Update Environment Variables

Edit the `.env` file with your actual values:

#### Required Variables
- `SECRET_KEY`: A secure secret key for Flask sessions (generate a strong random string)
- `DATABASE_URL`: Your database connection string

#### Optional Variables (with defaults)
- `SUPER_ADMIN_PASSWORD`: Password for super admin (default: superadmin123)
- `ADMIN_PASSWORD`: Password for school admin (default: admin123)
- `TEACHER_PASSWORD`: Password for teacher (default: teacher123)
- `PARENT_PASSWORD`: Password for parent (default: parent123)

#### Email Configuration
- `MAIL_SERVER`: SMTP server (e.g., smtp.gmail.com)
- `MAIL_USERNAME`: Your email username
- `MAIL_PASSWORD`: Your email password or app password
- `MAIL_DEFAULT_SENDER`: Default sender email

#### Payment Configuration (Paystack)
- `PAYSTACK_PUBLIC_KEY`: Your Paystack public key
- `PAYSTACK_SECRET_KEY`: Your Paystack secret key
- `PAYSTACK_WEBHOOK_SECRET`: Your webhook secret

### 3. Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use strong, unique passwords** for all accounts
3. **Generate a secure SECRET_KEY** using:
   ```python
   import secrets
   print(secrets.token_hex(32))
   ```
4. **Use environment-specific values** for production vs development
5. **Regularly rotate sensitive credentials**

### 4. Database Setup

The application will automatically create the database schema on first run. Ensure your database URL is correctly configured in the `.env` file.

### 5. Running the Application

```bash
python app.py
```

The application will:
- Load configuration from `.env` file
- Create necessary database tables
- Create default users if they don't exist
- Start the Flask development server

## File Structure

```
├── app.py                 # Main application file
├── config.py             # Configuration management
├── config.env.template   # Environment template
├── .env                  # Your environment variables (create this)
├── .gitignore           # Git ignore file
└── aiven_config.env     # Fallback configuration
```

## Troubleshooting

### Common Issues

1. **SECRET_KEY not set**: Ensure your `.env` file contains a valid SECRET_KEY
2. **Database connection failed**: Check your DATABASE_URL in `.env`
3. **Email not working**: Verify MAIL_* settings in `.env`
4. **Payment issues**: Check Paystack configuration in `.env`

### Getting Help

If you encounter issues:
1. Check that all required environment variables are set
2. Verify your database connection
3. Check the application logs for specific error messages
4. Ensure all dependencies are installed
