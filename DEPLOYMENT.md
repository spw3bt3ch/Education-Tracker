# SMIED Deployment Guide

## 🚀 Deploying to Render.com

### Prerequisites
1. GitHub account
2. Render.com account
3. Your code committed to Git

### Step 1: Push to GitHub

1. **Create a GitHub repository:**
   - Go to [GitHub.com](https://github.com)
   - Click "New repository"
   - Name it `smied` or similar
   - Make it private (recommended for security)

2. **Add GitHub remote and push:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/smied.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy to Render

1. **Connect to Render:**
   - Go to [Render.com](https://render.com)
   - Sign in with your GitHub account
   - Click "New +" → "Web Service"

2. **Configure the service:**
   - **Connect Repository:** Select your SMIED repository
   - **Name:** `smied` or `education-tracker`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python app.py`

3. **Environment Variables:**
   Add these in Render's environment variables section:
   ```
   DATABASE_URL=your_production_database_url
   SECRET_KEY=your_production_secret_key
   FLASK_ENV=production
   MAIL_SERVER=your_smtp_server
   MAIL_USERNAME=your_email
   MAIL_PASSWORD=your_email_password
   PAYSTACK_PUBLIC_KEY=your_paystack_public_key
   PAYSTACK_SECRET_KEY=your_paystack_secret_key
   ```

### Step 3: Update Live Application

After deployment, your changes will be live at:
- **Current URL:** https://education-tracker-98fb.onrender.com
- **Login Page:** https://education-tracker-98fb.onrender.com/login

## 🔄 Making Updates

1. **Make changes locally**
2. **Commit changes:**
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin main
   ```
3. **Render will automatically redeploy**

## 🔒 Security Checklist

- [ ] Remove all demo credentials from templates
- [ ] Use strong, unique SECRET_KEY
- [ ] Set up production database
- [ ] Configure production email settings
- [ ] Set up Paystack production keys
- [ ] Enable HTTPS (automatic on Render)
- [ ] Set up monitoring and logging

## 📝 Current Changes Ready for Deployment

✅ **Demo credentials removed from login page**
✅ **Professional "Need Help?" section added**
✅ **Setup scripts updated**
✅ **Security improvements implemented**

## 🚨 Important Notes

1. **Never commit `.env` files** - they contain sensitive data
2. **Use environment variables** in Render dashboard
3. **Test locally first** before deploying
4. **Monitor logs** after deployment
5. **Keep backups** of your database

## 🆘 Troubleshooting

### Common Issues:
1. **Build fails:** Check `requirements.txt` is complete
2. **Database connection fails:** Verify `DATABASE_URL` is correct
3. **Email not working:** Check SMTP settings
4. **Static files not loading:** Ensure proper file paths

### Getting Help:
- Check Render logs in dashboard
- Verify environment variables
- Test locally with production settings
- Contact support if needed

