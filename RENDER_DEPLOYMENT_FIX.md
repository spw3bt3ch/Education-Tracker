# 🔧 Render Deployment Fix - SQLite Configuration

## ❌ **Current Error**
```
Error in pricing route: (psycopg2.OperationalError) could not translate host name "pg-6e8de0c-smiwebsolutions08-5612.c.aivencloud.com" to address: Name or service not known
```

## ✅ **Solution: Switch to SQLite on Render**

### **Step 1: Update Render Environment Variables**

Go to your Render dashboard → Your App → Environment tab and update these variables:

#### **Remove these PostgreSQL variables:**
```
DATABASE_URL=postgresql://...
AIVEN_DB_HOST=...
AIVEN_DB_PORT=...
AIVEN_DB_NAME=...
AIVEN_DB_USER=...
AIVEN_DB_PASSWORD=...
AIVEN_DB_SSL_MODE=...
```

#### **Add these SQLite variables:**
```
DATABASE_URL=sqlite:///edutrack.db
SECRET_KEY=smied-production-secret-key-2024-change-in-production
FLASK_ENV=production
BASE_URL=https://your-app-name.onrender.com
DATABASE_TOTAL_CAPACITY_GB=1
```

### **Step 2: Update Your Render Build Command**

In your Render service settings, make sure your build command is:
```bash
pip install -r requirements.txt
```

### **Step 3: Update Your Start Command**

Make sure your start command is:
```bash
python app.py
```

### **Step 4: Redeploy**

After updating the environment variables, redeploy your app on Render.

## 🗄️ **Database Setup on Render**

The SQLite database will be created automatically when the app starts. The app will:

1. ✅ Create all database tables
2. ✅ Create default subscription plans
3. ✅ Create demo accounts (superadmin, admin, teacher, parent, student)

## 🔐 **Demo Login Credentials (After Deployment)**

- **Super Admin:** `superadmin` / `superadmin123`
- **School Admin:** `admin` / `admin123`
- **Teacher:** `teacher1` / `teacher123`
- **Parent:** `parent1` / `parent123`
- **Student:** `student1` / `student123`

## 💰 **Pricing Plans Available**

- **Free Trial:** ₦0 (7 days)
- **Monthly Plan:** ₦10,000 (30 days)
- **Annual Plan:** ₦100,000 (365 days)
- **Lifetime Plan:** ₦500,000 (Lifetime)

## 🚀 **Expected Result**

After the fix, your pricing page should work correctly and display all subscription plans without database connection errors.

## 📝 **Files to Update on GitHub**

1. **`.env`** - Local development configuration
2. **`RENDER_DEPLOYMENT_FIX.md`** - This deployment guide
3. **`config.env.example`** - Updated example configuration

## ⚠️ **Important Notes**

- SQLite databases on Render are ephemeral (they reset on each deployment)
- For production with persistent data, consider using Render's PostgreSQL service
- The current setup is perfect for demo/testing purposes
