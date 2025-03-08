# auth.py
# This module handles user account creation and login functionality.
# It includes the User class, functions for password validation, hashing,
# and file handling for storing user data.
# Modules used: os, sys, json, hashlib

import os  # OS module for file handling and checking file existence
import json  # For reading/writing user data in JSON format
import hashlib  # For password hashing

# Define the file path for storing user data
USER_DATA_FILE = os.path.join('data', 'users.json')

# User CLASS using functions and methods
class User: 
    def __init__(self, username, email, hashed_password):
        self.username = username
        self.email = email
        self.hashed_password = hashed_password

    def to_dict(self):
        # Convert the user object to a dictionary for JSON storage
        return {
            "username": self.username,
            "email": self.email,
            "hashed_password": self.hashed_password
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
    # Check for at least one special character
    special_characters = "!@#$%^&*()-+?_=,<>/"
    if not any(c in special_characters for c in password):
        return False, "Password must include at least one special character."
    return True, "Password is valid."

# Function to hash passwords using hashlib
def hash_password(password):
    # Create a sha256 hash object
    hash_object = hashlib.sha256()
    # Encode the password string and update the hash object
    hash_object.update(password.encode('utf-8'))
    # Return the hexadecimal digest of the hash
    return hash_object.hexdigest()

# Function to create a new user account
def create_user(username, password, email):
    # Validate the password
    is_valid, message = validate_password(password)
    if not is_valid:
        return message

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
        return "Username already exists."

    # Add the new user to the users dictionary
    users[username] = new_user.to_dict()

    # Write the updated user data back to the JSON file (file handling)
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f, indent=4)

    return "User account created successfully."

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

    # Get the stored hashed password for the user
    stored_hashed = users[username]['hashed_password']
    # Hash the provided password
    provided_hashed = hash_password(password)
    # Casting both to strings before comparing (demonstrating casting)
    if str(stored_hashed) == str(provided_hashed):
        return True
    else:
        return False