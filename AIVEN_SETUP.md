# SMIED Aiven Database Setup Guide

## 🔒 Secure Setup Options

### Option 1: Interactive Secure Setup (Recommended)

Use the interactive setup script that prompts for sensitive information:

```bash
python secure_setup.py
```

**Features:**
- ✅ Prompts for sensitive data (passwords not displayed)
- ✅ Generates secure secret key automatically
- ✅ Validates required configuration
- ✅ Creates secure .env file
- ✅ No sensitive data in source code

### Option 2: Template-Based Setup

1. **Copy the template:**
   ```bash
   cp aiven_setup.env.template .env
   ```

2. **Edit .env with your Aiven details:**
   ```bash
   # Update these values with your actual Aiven database details
   DATABASE_URL=postgresql://username:password@host:port/database?sslmode=require
   AIVEN_DB_HOST=your-db-host.aivencloud.com
   AIVEN_DB_PORT=27725
   AIVEN_DB_NAME=your_database_name
   AIVEN_DB_USER=avnadmin
   AIVEN_DB_PASSWORD=your_db_password
   ```

3. **Generate a secure secret key:**
   ```python
   import secrets
   print(secrets.token_hex(32))
   ```

### Option 3: Automated Setup (Legacy)

If you have existing configuration in `aiven_config.env`:

```bash
python setup_with_aiven.py
```

## 📊 Required Aiven Database Information

You'll need the following information from your Aiven dashboard:

- **Host**: Your Aiven database host (e.g., `pg-xxx-xxx.aivencloud.com`)
- **Port**: Database port (usually `27725`)
- **Database Name**: Your database name
- **Username**: Usually `avnadmin`
- **Password**: Your Aiven database password
- **SSL Mode**: Usually `require`

## 🔧 Configuration Details

### Database Configuration
```env
DATABASE_URL=postgresql://username:password@host:port/database?sslmode=require
AIVEN_DB_HOST=your-db-host.aivencloud.com
AIVEN_DB_PORT=27725
AIVEN_DB_NAME=your_database_name
AIVEN_DB_USER=avnadmin
AIVEN_DB_PASSWORD=your_db_password
AIVEN_DB_SSL_MODE=require
```

### Flask Configuration
```env
SECRET_KEY=your-secret-key-here-change-this-in-production
FLASK_ENV=production
```

### Email Configuration (Optional)
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

### Payment Configuration (Optional)
```env
PAYSTACK_PUBLIC_KEY=pk_live_your_public_key
PAYSTACK_SECRET_KEY=sk_live_your_secret_key
PAYSTACK_WEBHOOK_SECRET=your_webhook_secret
```

## 🚀 Running the Application

After setup:

```bash
python app.py
```

The application will:
- Load configuration from .env file
- Connect to your Aiven database
- Create necessary tables
- Start the Flask development server

## 🔒 Security Best Practices

1. **Never commit .env files** to version control
2. **Use strong, unique passwords** for all accounts
3. **Generate a secure SECRET_KEY** using the interactive setup
4. **Regularly rotate sensitive credentials**
5. **Use environment-specific values** for production vs development

## 🛠️ Troubleshooting

### Common Issues

1. **Database connection failed:**
   - Check your Aiven database is running
   - Verify host, port, and credentials
   - Ensure SSL mode is correct

2. **SECRET_KEY not set:**
   - Use the interactive setup script
   - Or manually generate one: `python -c "import secrets; print(secrets.token_hex(32))"`

3. **Email not working:**
   - Verify SMTP settings
   - Check if using app passwords for Gmail
   - Ensure firewall allows SMTP connections

4. **Payment issues:**
   - Verify Paystack configuration
   - Check API keys are correct
   - Ensure webhook URL is accessible

### Getting Help

If you encounter issues:
1. Check that all required environment variables are set
2. Verify your Aiven database connection
3. Check the application logs for specific error messages
4. Ensure all dependencies are installed

## 📁 File Structure

```
├── secure_setup.py           # Interactive secure setup
├── setup_with_aiven.py       # Automated setup (legacy)
├── aiven_setup.env.template  # Aiven configuration template
├── config.env.template       # General configuration template
├── .env                      # Your environment variables (create this)
├── .gitignore               # Updated with security exclusions
└── AIVEN_SETUP.md           # This guide
```

## 🎯 Quick Start

1. **Run interactive setup:**
   ```bash
   python secure_setup.py
   ```

2. **Start the application:**
   ```bash
   python app.py
   ```

3. **Open your browser:**
   ```
   http://localhost:5000
   ```

4. **Login with your configured credentials**

That's it! Your SMIED application is now securely configured with Aiven.
