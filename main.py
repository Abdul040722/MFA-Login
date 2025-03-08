# main.py
# This file is the entry point for the MFA system.
# It uses Flask to provide routes for user login, registration, and OTP verification.
# Modules used: os, auth, otp
# Functions, error handling, and file handling are used where appropriate.

from flask import Flask, render_template, request, redirect, url_for, flash
import os  # Module for operating system interaction
import auth  # Our authentication module (contains User class, registration, login functions)
import otp   # Module for generating one-time passwords

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flashing messages

# Route for the home/login page
@app.route('/')
def index():
    return render_template('index.html')

# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register(): # Function for user registration
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        # Call create_user function from auth module
        message = auth.create_user(username, password, email)
        flash(message)
        return redirect(url_for('register'))
    return render_template('register.html')

# Route for user login
@app.route('/login', methods=['POST'])
def login():
    # Retrieve login credentials
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Validate credentials using auth module
    if auth.check_user_credentials(username, password):
        # Generate OTP for additional authentication step
        generated_otp = otp.generate_otp()
        print(f"Generated OTP for {username}: {generated_otp}")
        # Store OTP in session or temporary storage (here we pass it via query parameter for simplicity)
        return redirect(url_for('verify_otp', otp_value=generated_otp, user=username))
    else:
        flash("Invalid username or password.")
        return redirect(url_for('index'))

# Route for OTP verification
@app.route('/otp', methods=['GET', 'POST'])
def verify_otp():
    # Get OTP and user from query parameters (this is a simplified demonstration)
    otp_value = request.args.get('otp_value')
    user = request.args.get('user')
    
    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        # Compare the entered OTP with the generated OTP (casting to string for safety)
        if str(entered_otp) == str(otp_value):
            flash(f"Welcome {user}! Login successful with OTP verification.")
            return redirect(url_for('index'))
        else:
            flash("Incorrect OTP. Please try again.")
            return redirect(url_for('verify_otp', otp_value=otp_value, user=user))
    
    return render_template('otp.html', otp_value=otp_value, user=user)

if __name__ == '__main__':
    # Check if the required data directory exists; if not, create it.
    if not os.path.exists('data'):
        os.makedirs('data')
    # Run the Flask application
    app.run(debug=True)