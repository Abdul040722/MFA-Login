# main.py
# Modules used: os, auth, otp, flask, session_manager, email_service, security_logger, rate_limiter

from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import auth
import otp
from session_manager import SessionManager
from email_service import send_otp_email
from security_logger import log_login_attempt, log_otp_validation, log_security_event, log_rate_limit_trigger
from rate_limiter import RateLimiter

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')  # Better to use environment variable

# Initialize session manager and rate limiter
session_manager = SessionManager()
rate_limiter = RateLimiter()

# Clean up expired sessions on startup and periodically
cleanup_done = False

@app.before_request
def before_request():
    global cleanup_done
    if not cleanup_done:
        session_manager.cleanup_expired_sessions()
        cleanup_done = True

# Route for the home/login page
@app.route('/')
def index():
    return render_template('index.html')

# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get client IP for rate limiting and logging
        client_ip = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        
        # Check rate limit for registration attempts
        is_allowed, message, _ = rate_limiter.check_rate_limit(f"reg_{client_ip}", "login")
        if not is_allowed:
            log_rate_limit_trigger(client_ip, None, "registration", message)
            flash(message)
            return redirect(url_for('register'))
        
        # Get form data
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        
        # Call create_user function from auth module
        message, status = auth.create_user(username, password, email)
        
        # Log the registration attempt
        log_login_attempt(
            username, 
            client_ip, 
            user_agent, 
            "SUCCESS" if status else "FAIL", 
            message
        )
        
        flash(message)
        if status:
            return redirect(url_for('index'))
        return redirect(url_for('register'))
    
    return render_template('register.html')

# Route for user login
@app.route('/login', methods=['POST'])
def login():
    # Get client IP and user agent for rate limiting and logging
    client_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    
    # Retrieve login credentials
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Check rate limit for login attempts
    is_allowed, message, _ = rate_limiter.check_rate_limit(f"login_{client_ip}", "login")
    if not is_allowed:
        log_rate_limit_trigger(client_ip, username, "login", message)
        flash(message)
        return redirect(url_for('index'))
    
    # Also check rate limit for this specific username
    is_allowed, message, _ = rate_limiter.check_rate_limit(f"login_user_{username}", "login")
    if not is_allowed:
        log_rate_limit_trigger(client_ip, username, "login", message)
        flash(message)
        return redirect(url_for('index'))
    
    # Validate credentials using auth module
    if auth.check_user_credentials(username, password):
        # Check if user already has an active session
        has_active, session_id = session_manager.has_active_session(username)
        if has_active:
            # Invalidate existing session
            session_manager.invalidate_session(session_id)
            log_security_event("SESSION_INVALIDATED", username, client_ip, 
                              "New login attempt while session is active")
        
        # Get user's email from the users data
        user_data = auth.get_user_data(username)
        if not user_data:
            log_login_attempt(username, client_ip, user_agent, "FAIL", "User data not found")
            flash("An error occurred. Please try again.")
            return redirect(url_for('index'))
        
        email = user_data['email']
        
        # Check rate limit for email sending
        is_allowed, message, _ = rate_limiter.check_rate_limit(f"email_{email}", "email")
        if not is_allowed:
            log_rate_limit_trigger(client_ip, username, "email", message)
            flash(message)
            return redirect(url_for('index'))
        
        # Generate OTP for additional authentication step
        generated_otp = otp.generate_otp()
        
        # Create a new session
        session_id = session_manager.create_session(username, generated_otp, client_ip, user_agent)
        
        # Send OTP via email
        success, message = send_otp_email(email, generated_otp, username)
        
        if not success:
            # Log failure
            log_security_event("OTP_DELIVERY_FAILED", username, client_ip, message)
            # Flash message to user
            flash(message)
            return redirect(url_for('index'))
        
        # Log successful login attempt
        log_login_attempt(username, client_ip, user_agent, "SUCCESS", "Proceeding to OTP verification")
        
        # Redirect to OTP verification page
        return redirect(url_for('verify_otp', session_id=session_id))
    else:
        # Log failed login attempt
        log_login_attempt(username, client_ip, user_agent, "FAIL", "Invalid credentials")
        flash("Invalid username or password.")
        return redirect(url_for('index'))

# Route for OTP verification
@app.route('/otp/<session_id>', methods=['GET', 'POST'])
def verify_otp(session_id):
    client_ip = request.remote_addr
    
    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        
        # Check rate limit for OTP verification attempts
        is_allowed, message, _ = rate_limiter.check_rate_limit(f"otp_{client_ip}", "otp")
        if not is_allowed:
            log_rate_limit_trigger(client_ip, None, "otp_verification", message)
            flash(message)
            return redirect(url_for('verify_otp', session_id=session_id))
        
        # Validate OTP
        is_valid, message = session_manager.validate_otp(session_id, entered_otp, client_ip)
        
        # Get session data for logging (username)
        session_file = os.path.join(session_manager.SESSION_DIR, f"{session_id}.json")
        username = None
        if os.path.exists(session_file):
            import json
            with open(session_file, "r") as f:
                session_data = json.load(f)
                username = session_data.get("username")
        
        # Log OTP validation attempt
        log_otp_validation(
            username or "unknown", 
            session_id, 
            client_ip, 
            "SUCCESS" if is_valid else "FAIL", 
            message
        )
        
        if is_valid:
            # Invalidate session after successful verification
            session_manager.invalidate_session(session_id)
            flash(f"Welcome {username}! Login successful with OTP verification.")
            # Here you would typically create a user session in Flask
            session['user'] = username
            session['authenticated'] = True
            return redirect(url_for('dashboard'))
        else:
            flash(message)
            return redirect(url_for('verify_otp', session_id=session_id))
    
    return render_template('otp.html', session_id=session_id)

# Dashboard route (protected)
@app.route('/dashboard')
def dashboard():
    # Check if user is authenticated
    if not session.get('authenticated'):
        flash("Please login to access the dashboard.")
        return redirect(url_for('index'))
    
    username = session.get('user')
    return render_template('dashboard.html', username=username)

# Logout route
@app.route('/logout')
def logout():
    # Clear session
    session.pop('user', None)
    session.pop('authenticated', None)
    flash("You have been successfully logged out.")
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Ensure required directories exist
    for directory in ['data', 'logs']:
        if not os.path.exists(directory):
            os.makedirs(directory)
    
# Print the URL for clarity
    print("App running at: http://127.0.0.1:5000/")
    
    # Run the Flask application
    app.run(debug=True, host='0.0.0.0', port=5000)