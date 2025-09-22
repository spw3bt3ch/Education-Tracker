# Email Configuration Guide for EduTrack

This guide will help you set up email functionality for your Student Assignment Tracking App.

## 📧 Email Features

The email system includes:
- Welcome emails for new users
- School registration confirmations
- Password reset emails
- Assignment notifications to parents
- Grade notifications
- System notifications
- Teacher and parent invitations

## 🔧 Configuration Steps

### 1. Install Email Dependencies

```bash
pip install Flask-Mail==0.9.1
```

### 2. Email Provider Setup

#### Option A: Gmail (Recommended for Development)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate an App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a password for "Mail"
3. **Update your `.env` file**:

```env
# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-character-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
MAIL_MAX_EMAILS=100
MAIL_SUPPRESS_SEND=False
BASE_URL=http://127.0.0.1:5000
```

#### Option B: Other SMTP Providers

**Outlook/Hotmail:**
```env
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
```

**Yahoo:**
```env
MAIL_SERVER=smtp.mail.yahoo.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
```

**Custom SMTP:**
```env
MAIL_SERVER=your-smtp-server.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=your-username
MAIL_PASSWORD=your-password
```

### 3. Production Email Services

For production, consider these reliable email services:

#### SendGrid
```env
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
```

#### Mailgun
```env
MAIL_SERVER=smtp.mailgun.org
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-mailgun-username
MAIL_PASSWORD=your-mailgun-password
```

#### Amazon SES
```env
MAIL_SERVER=email-smtp.us-east-1.amazonaws.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-ses-username
MAIL_PASSWORD=your-ses-password
```

## 🧪 Testing Email Configuration

### 1. Test Route
Visit: `http://127.0.0.1:5000/test-email`

### 2. Manual Testing
```python
from email_service import test_email_configuration
test_email_configuration()
```

### 3. Check Logs
Monitor the console for email sending status and any errors.

## 📧 Email Templates

The system includes these email templates:

- **welcome.html** - New user welcome
- **school_registration.html** - School registration confirmation
- **password_reset.html** - Password reset instructions
- **assignment_notification.html** - New assignment alerts
- **assignment_submission.html** - Submission notifications
- **grade_notification.html** - Grade posting alerts

## 🔒 Security Considerations

### 1. Environment Variables
- Never commit email credentials to version control
- Use strong, unique passwords
- Rotate credentials regularly

### 2. Rate Limiting
- The system includes built-in rate limiting
- Set `MAIL_MAX_EMAILS` to prevent spam
- Monitor email sending patterns

### 3. Error Handling
- All email sending is wrapped in try-catch blocks
- Failed emails are logged but don't break the application
- Graceful degradation when email service is unavailable

## 🚀 Production Deployment

### 1. Environment Variables
Set these in your production environment:
```bash
export MAIL_SERVER=smtp.your-provider.com
export MAIL_USERNAME=your-username
export MAIL_PASSWORD=your-password
export MAIL_DEFAULT_SENDER=noreply@yourdomain.com
export BASE_URL=https://yourdomain.com
```

### 2. Email Service Provider
- Use a dedicated email service for production
- Set up proper SPF, DKIM, and DMARC records
- Monitor delivery rates and reputation

### 3. Monitoring
- Set up email delivery monitoring
- Track bounce rates and spam complaints
- Monitor email queue performance

## 📱 Email Features in Action

### Automatic Emails Sent:
1. **School Registration** - Confirmation to admin
2. **User Registration** - Welcome email
3. **Assignment Created** - Notification to parents
4. **Assignment Submitted** - Notification to teacher
5. **Grade Posted** - Notification to parents
6. **Password Reset** - Reset instructions

### Manual Email Triggers:
- System notifications
- Teacher invitations
- Parent invitations
- Custom announcements

## 🛠️ Troubleshooting

### Common Issues:

1. **Authentication Failed**
   - Check username/password
   - Verify 2FA is enabled (Gmail)
   - Use app password instead of regular password

2. **Connection Refused**
   - Check SMTP server and port
   - Verify firewall settings
   - Test network connectivity

3. **Emails Not Sending**
   - Check `MAIL_SUPPRESS_SEND` setting
   - Verify email addresses are valid
   - Check spam folder

4. **Template Errors**
   - Ensure all email templates exist
   - Check template syntax
   - Verify template variables

### Debug Mode:
```python
app.config['MAIL_DEBUG'] = True
```

## 📊 Email Analytics

Consider integrating email analytics to track:
- Delivery rates
- Open rates
- Click-through rates
- Bounce rates
- Unsubscribe rates

## 🔄 Email Queue (Optional)

For high-volume applications, consider implementing:
- Redis-based email queue
- Celery for background processing
- Email retry mechanisms
- Dead letter queue for failed emails

---

## 📞 Support

If you encounter issues with email configuration:
1. Check the logs for specific error messages
2. Verify your email provider settings
3. Test with a simple email first
4. Contact your email provider's support

The email system is designed to be robust and fail gracefully, ensuring your application continues to work even if email services are temporarily unavailable.
