# Secure MFA System

A secure Multi-Factor Authentication (MFA) web application built with Flask, featuring user registration, OTP verification via email, rate limiting, and comprehensive security logging.

## Features

- **User Registration**: Password validation with complexity requirements (uppercase, lowercase, numbers, special characters)
- **MFA Login Flow**: Password + One-Time Password (OTP) sent via email
- **Session Management**: Secure session handling with automatic expiration
- **Rate Limiting**: Protection against brute-force attacks on login/registration/OTP endpoints
- **Security Logging**: Detailed logging of authentication attempts and security events
- **Email Integration**: SMTP-based OTP delivery via smtp2go with retry mechanism
- **Dashboard**: Protected user dashboard with security status and activity tracking
- **Password Security**: SHA-256 hashing with salt
- **Responsive UI**: Clean and modern interface with client-side validation

## Installation

1. **Clone Repository**
   ```bash
   git clone https://github.com/Abdul040722/MFA-Login
   cd MFA-Login
   ```

2. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate    # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install flask python-dotenv
   ```

4. **Create Required Directories**
   ```bash
   mkdir -p data logs static data/sessions
   ```

## Configuration

1. **Environment Variables** (create `.env` file)
   ```env
   SECRET_KEY=your_secure_secret_key
   SMTP_SERVER=your.smtp.server
   SMTP_PORT=587
   SMTP_USERNAME=your_smtp_username
   SMTP_PASSWORD=your_smtp_password
   SENDER_EMAIL=noreply@yourdomain.com
   ```

2. **Email Service Setup**
   - Update SMTP credentials in `email_service.py`
   - Test email functionality before deployment

## Usage

1. **Start Application**
   ```bash
   python main.py
   ```

2. **Access in Browser**
   ```
   http://localhost:5000
   ```

3. **User Flow**
   - Register new account with valid email
   - Login with username/password
   - Check email for OTP and verify
   - Access secure dashboard
   - Logout when finished

## Project Structure

```
├── data/                # user & session data
    ├── sessions/
    ├── users.json
├── logs                 # logs security details
└── static/              # Frontend assets
    ├── style.css
    └── script.js
├── templates/           # HTML templates
│   ├── index.html
│   ├── register.html
│   ├── otp.html
│   └── dashboard.html
├── main.py              # Main application entry point
├── auth.py              # User authentication and management
├── otp.py               # OTP generation and validation
├── email_service.py     # Email delivery functionality
├── rate_limiter.py      # Rate limiting implementation
├── security_logger.py   # Security event logging
├── session_manager.py   # Session handling logic
```

## Dependencies

- Python 3.8+
- Flask
- smtplib (Python standard library)
- Additional Python libraries: hashlib, uuid, logging, json

## Security Features

- **Password Hashing**: SHA-256 with salt
- **Account Lockout**: 5 failed attempts locks account for 30 minutes
- **Session Security**:
  - Automatic session expiration (10 minutes)
  - Single active session per user
  - Session invalidation on logout
- **Rate Limiting**:
  - 5 login attempts/5 minutes
  - 3 OTP attempts/10 minutes
  - Progressive lockout durations
- **Security Logging**:
  - Authentication attempts (success/failure)
  - OTP validation attempts
  - Rate limit triggers
  - Session events

## License