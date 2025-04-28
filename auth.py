# auth.py
# Modules used: os, json, hashlib, re

import os
import json
import hashlib
import re
import time

# Define the file path for storing user data
USER_DATA_FILE = os.path.join('data', 'users.json')

# User CLASS using functions and methods
class User: 
    def __init__(self, username, email, hashed_password):
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.locked = False
        self.lock_expiry = 0
        self.failed_attempts = 0
        self.last_login = 0

    def to_dict(self):
        # Convert the user object to a dictionary for JSON storage
        return {
            "username": self.username,
            "email": self.email,
            "hashed_password": self.hashed_password,
            "locked": self.locked,
            "lock_expiry": self.lock_expiry,
            "failed_attempts": self.failed_attempts,
            "last_login": self.last_login
        }

# Function to validate password according to the requirements:
# Minimum length, inclusion of special characters, and mix of uppercase/lowercase letters.
def validate_password(password):
    # Minimum length requirement
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    # Check for at least one uppercase letter
    if not any(c.isupper() for c in password):
        return False, "Password must include at least one uppercase letter."
    # Check for at least one lowercase letter
    if not any(c.islower() for c in password):
        return False, "Password must include at least one lowercase letter."
    # Check for at least one digit
    if not any(c.isdigit() for c in password):
        return False, "Password must include at least one number."
    # Check for at least one special character
    special_characters = "!@#$%^&*()-+?_=,<>/"
    if not any(c in special_characters for c in password):
        return False, "Password must include at least one special character."
    return True, "Password is valid."

# Function to validate email format
def validate_email(email):
    # Basic email validation regex
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(email_regex, email):
        return True
    return False

# Function to hash passwords using hashlib with added salt
def hash_password(password):
    # Salt could be stored per user in a production system
    salt = "mfa_system_salt"  # In a real system, use a unique salt per user
    # Create a sha256 hash object
    hash_object = hashlib.sha256()
    # Combine password with salt and update the hash object
    hash_object.update((password + salt).encode('utf-8'))
    # Return the hexadecimal digest of the hash
    return hash_object.hexdigest()

# Function to create a new user account
def create_user(username, password, email):
    # Validate the username
    if not username or len(username) < 3:
        return "Username must be at least 3 characters long.", False
    
    # Validate the email
    if not validate_email(email):
        return "Invalid email format.", False
    
    # Validate the password
    is_valid, message = validate_password(password)
    if not is_valid:
        return message, False

    # Hash the password
    hashed = hash_password(password)

    # Create a new user object
    new_user = User(username, email, hashed)
    
    # Read existing users from the JSON file (FILE HANDLING)
    users = {}
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            try:
                users = json.load(f)
            except json.JSONDecodeError:
                users = {}

    # Check if the username already exists
    if username in users:
        return "Username already exists.", False
    
    # Check if the email already exists
    for existing_user in users.values():
        if existing_user['email'] == email:
            return "Email address is already registered.", False

    # Add the new user to the users dictionary
    users[username] = new_user.to_dict()

    # Write the updated user data back to the JSON file (file handling)
    try:
        with open(USER_DATA_FILE, 'w') as f:
            json.dump(users, f, indent=4)
        return "User account created successfully.", True
    except Exception as e:
        return f"Error creating user account: {str(e)}", False

# Function to check user credentials during login
def check_user_credentials(username, password):
    if not os.path.exists(USER_DATA_FILE):
        return False

    with open(USER_DATA_FILE, 'r') as f:
        try:
            users = json.load(f)
        except json.JSONDecodeError:
            return False

    if username not in users:
        return False
    
    # Check if account is locked
    user_data = users[username]
    if user_data.get('locked', False):
        lock_expiry = user_data.get('lock_expiry', 0)
        current_time = int(time.time())
        
        if current_time < lock_expiry:
            # Account is still locked
            return False
        else:
            # Lock period expired, reset lock status
            user_data['locked'] = False
            user_data['lock_expiry'] = 0
            user_data['failed_attempts'] = 0
            with open(USER_DATA_FILE, 'w') as f:
                json.dump(users, f, indent=4)

    # Get the stored hashed password for the user
    stored_hashed = user_data['hashed_password']
    # Hash the provided password
    provided_hashed = hash_password(password)
    # Casting both to strings before comparing (demonstrating casting)
    if str(stored_hashed) == str(provided_hashed):
        # Reset failed attempts on successful login
        user_data['failed_attempts'] = 0
        user_data['last_login'] = int(time.time())
        with open(USER_DATA_FILE, 'w') as f:
            json.dump(users, f, indent=4)
        return True
    else:
        # Increment failed attempts
        user_data['failed_attempts'] = user_data.get('failed_attempts', 0) + 1
        
        # Lock account after too many failed attempts
        if user_data['failed_attempts'] >= 5:
            user_data['locked'] = True
            # Lock for 30 minutes
            user_data['lock_expiry'] = int(time.time()) + 1800
            
        with open(USER_DATA_FILE, 'w') as f:
            json.dump(users, f, indent=4)
        return False

# Function to get user data by username
def get_user_data(username):
    if not os.path.exists(USER_DATA_FILE):
        return None

    with open(USER_DATA_FILE, 'r') as f:
        try:
            users = json.load(f)
        except json.JSONDecodeError:
            return None

    return users.get(username)