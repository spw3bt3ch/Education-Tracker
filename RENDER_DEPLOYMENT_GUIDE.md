# 🚀 Render Deployment Guide - Education Tracker

## ❌ **Common Issues & Solutions**

### **Issue 1: "No environment configuration file found!"**
**Solution:** The app now automatically detects production environments and uses system environment variables instead of .env files.

### **Issue 2: "Could not translate host name" (PostgreSQL Error)**
**Solution:** Switch to SQLite for simpler deployment.

## 🔧 **Step-by-Step Render Deployment**

### **Step 1: Set Environment Variables in Render**

Go to your Render dashboard → Your App → Environment tab and set these variables:

#### **Required Variables:**
```
DATABASE_URL=sqlite:///edutrack.db
SECRET_KEY=your-super-secret-key-here-change-this-in-production
FLASK_ENV=production
BASE_URL=https://education-tracker-98fb.onrender.com
```

#### **Optional Variables:**
```
DATABASE_TOTAL_CAPACITY_GB=1
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### **Step 2: Build & Deploy Settings**

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
python app.py
```

### **Step 3: Deploy**

Click "Deploy" in your Render dashboard.

## ✅ **Expected Results After Deployment**

### **✅ Pricing Page Should Show:**
- Free Trial: ₦0 (7 days)
- Monthly Plan: ₦10,000 (30 days)
- Annual Plan: ₦100,000 (365 days)
- Lifetime Plan: ₦500,000 (Lifetime)

### **✅ Demo Login Credentials:**
- **Super Admin:** `superadmin` / `superadmin123`
- **School Admin:** `admin` / `admin123`
- **Teacher:** `teacher1` / `teacher123`
- **Parent:** `parent1` / `parent123`
- **Student:** `student1` / `student123`

## 🔍 **Troubleshooting**

### **If Pricing Plans Still Don't Show:**
1. Check Render logs for database errors
2. Verify environment variables are set correctly
3. Ensure `DATABASE_URL=sqlite:///edutrack.db` is set

### **If App Won't Start:**
1. Check that `SECRET_KEY` is set
2. Verify `FLASK_ENV=production` is set
3. Check build logs for Python package installation errors

## 📁 **Files Updated for This Fix**

1. **`config.py`** - ✅ **UPDATED** - Now handles production environments properly
2. **`RENDER_DEPLOYMENT_GUIDE.md`** - ✅ **NEW** - This deployment guide
3. **`.env`** - ✅ **LOCAL ONLY** - For local development

## 🎯 **Key Changes Made**

- ✅ **Fixed config.py** to detect production environments
- ✅ **Removed .env dependency** for production deployments
- ✅ **Updated default database** to use `edutrack.db`
- ✅ **Added production environment detection**

## 🚀 **Deployment Checklist**

- [ ] Environment variables set in Render
- [ ] Build command configured
- [ ] Start command configured
- [ ] App deployed successfully
- [ ] Pricing page shows plans
- [ ] Demo accounts work

Your app should now deploy successfully on Render without the environment configuration errors!
