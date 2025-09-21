# Aiven Cloud Database Migration Guide

This guide will help you migrate your Student Assignment Tracking App from SQLite to Aiven cloud database (PostgreSQL or MySQL).

## 📋 Prerequisites

1. **Aiven Account**: Sign up at [aiven.io](https://aiven.io) if you don't have one
2. **Python Environment**: Ensure Python 3.7+ is installed
3. **Current App**: Your Student Assignment Tracking App should be working with SQLite

## 🚀 Step 1: Set Up Aiven Database

### 1.1 Create Aiven Service

1. Log in to [Aiven Console](https://console.aiven.io)
2. Click "Create Service"
3. Choose either:
   - **PostgreSQL** (Recommended)
   - **MySQL**
4. Select your preferred cloud provider and region
5. Choose a service plan based on your needs
6. Give your service a name (e.g., "edutrack-db")
7. Click "Create Service"

### 1.2 Get Connection Details

Once your service is created:

1. Go to your service dashboard
2. Click on "Connection information"
3. Copy the connection details:
   - **Host**
   - **Port**
   - **Database name**
   - **Username**
   - **Password**

## 🔧 Step 2: Configure Your Application

### 2.1 Install Dependencies

```bash
# Install new dependencies
pip install -r requirements.txt
```

### 2.2 Set Up Environment Variables

1. Copy the example configuration:
   ```bash
   cp config.env.example .env
   ```

2. Edit `.env` file with your Aiven connection details:

   **For PostgreSQL:**
   ```env
   DATABASE_URL=postgresql://username:password@hostname:port/database_name
   SECRET_KEY=your-secret-key-here
   FLASK_ENV=production
   ```

   **For MySQL:**
   ```env
   DATABASE_URL=mysql://username:password@hostname:port/database_name
   SECRET_KEY=your-secret-key-here
   FLASK_ENV=production
   ```

   **Example with actual values:**
   ```env
   DATABASE_URL=postgresql://avnadmin:your_password@pg-abc123-def456.aivencloud.com:12345/defaultdb
   SECRET_KEY=your-super-secret-key-here
   FLASK_ENV=production
   ```

## 📦 Step 3: Migrate Your Data

### 3.1 Export Data from SQLite

```bash
# Export data from your current SQLite database
python migrate_to_aiven.py --export-only
```

This creates a `migration_data.json` file with all your data.

### 3.2 Set Up Aiven Database Tables

```bash
# Create tables in Aiven database
python setup_aiven.py
```

### 3.3 Import Data to Aiven

```bash
# For PostgreSQL
python migrate_to_aiven.py --target postgres

# For MySQL
python migrate_to_aiven.py --target mysql
```

### 3.4 Verify Migration

```bash
# Test database connection
python setup_aiven.py --test-only
```

## 🎯 Step 4: Update Your Application

### 4.1 Test with Aiven Database

```bash
# Run your application
python app.py
```

### 4.2 Verify Everything Works

1. Open your browser to `http://localhost:5000`
2. Login with your admin credentials
3. Check that all data is present
4. Test creating new records

## 🔄 Alternative Migration Methods

### Method 1: Complete Migration (Recommended)
```bash
# One command to migrate everything
python migrate_to_aiven.py --target postgres
```

### Method 2: Step-by-Step Migration
```bash
# Step 1: Export data
python migrate_to_aiven.py --export-only

# Step 2: Setup database
python setup_aiven.py

# Step 3: Import data
python migrate_to_aiven.py --import-only --target postgres
```

### Method 3: Manual Migration
If you prefer to migrate manually:

1. Export data: `python migrate_to_aiven.py --export-only`
2. Set up Aiven database tables: `python setup_aiven.py`
3. Use Aiven's migration tools in the console
4. Import your data using Aiven's tools

## 🛠️ Troubleshooting

### Common Issues

#### 1. Connection Errors
```
Error: could not connect to server
```
**Solution:**
- Check your DATABASE_URL format
- Verify Aiven service is running
- Check firewall settings
- Ensure SSL is properly configured

#### 2. Authentication Errors
```
Error: authentication failed
```
**Solution:**
- Verify username and password
- Check if user has proper permissions
- Ensure database name is correct

#### 3. SSL Errors
```
Error: SSL connection required
```
**Solution:**
- Add `?sslmode=require` to PostgreSQL URL
- For MySQL, ensure SSL is enabled in connection

#### 4. Table Creation Errors
```
Error: relation already exists
```
**Solution:**
- Use `--force` flag: `python setup_aiven.py --force`
- Or manually drop tables in Aiven console

### Debugging Commands

```bash
# Test database connection
python setup_aiven.py --test-only

# Check migration data
python -c "import json; data=json.load(open('migration_data.json')); print(f'Tables: {list(data.keys())}')"

# Verify table structure
python -c "from app import app, db; app.app_context().push(); print(db.inspect(db.engine).get_table_names())"
```

## 📊 Migration Script Options

### migrate_to_aiven.py Options

```bash
# Export only (no import)
python migrate_to_aiven.py --export-only

# Import only (from existing export file)
python migrate_to_aiven.py --import-only --target postgres

# Complete migration
python migrate_to_aiven.py --target postgres

# Use custom export file
python migrate_to_aiven.py --export-file my_data.json --target postgres
```

### setup_aiven.py Options

```bash
# Test connection only
python setup_aiven.py --test-only

# Force recreate tables (WARNING: deletes data)
python setup_aiven.py --force
```

## 🔒 Security Best Practices

1. **Environment Variables**: Never commit `.env` file to version control
2. **Strong Passwords**: Use strong, unique passwords for Aiven
3. **SSL**: Always use SSL connections in production
4. **Access Control**: Limit database access to necessary IPs
5. **Backups**: Enable automatic backups in Aiven

## 📈 Performance Optimization

### Aiven Service Configuration

1. **Choose Right Plan**: Select appropriate service plan for your usage
2. **Connection Pooling**: Consider using connection pooling for high traffic
3. **Indexing**: Monitor query performance and add indexes as needed
4. **Monitoring**: Use Aiven's monitoring tools to track performance

### Application Configuration

```python
# In your .env file, you can add:
SQLALCHEMY_ENGINE_OPTIONS='{"pool_size": 10, "pool_recycle": 3600}'
```

## 🆘 Support

### Getting Help

1. **Aiven Documentation**: [docs.aiven.io](https://docs.aiven.io)
2. **Aiven Support**: Available through Aiven Console
3. **Community**: [Aiven Community Forum](https://community.aiven.io)

### Migration Script Issues

If you encounter issues with the migration scripts:

1. Check Python version (3.7+ required)
2. Verify all dependencies are installed
3. Check file permissions
4. Review error messages carefully

## ✅ Post-Migration Checklist

- [ ] Database connection working
- [ ] All tables created successfully
- [ ] Data migrated completely
- [ ] Application starts without errors
- [ ] Login functionality works
- [ ] All features tested
- [ ] Performance acceptable
- [ ] Backups configured
- [ ] Monitoring set up
- [ ] Old SQLite database backed up

## 🎉 Congratulations!

You've successfully migrated your Student Assignment Tracking App to Aiven cloud database! Your application now benefits from:

- **Scalability**: Easy to scale up/down as needed
- **Reliability**: Managed service with high availability
- **Security**: Enterprise-grade security features
- **Backups**: Automatic backups and point-in-time recovery
- **Monitoring**: Built-in monitoring and alerting
- **Global**: Deploy in multiple regions worldwide

---

**Need Help?** If you encounter any issues during migration, please check the troubleshooting section above or contact support.
