# session_manager.py
# Modules used: uuid, time, json, os, hashlib

import uuid
import time
import json
import os
import hashlib
from datetime import datetime

# Directory for session storage
SESSION_DIR = "data/sessions"
# OTP expiration time in seconds (10 minutes)
OTP_EXPIRY = 600

class SessionManager:
    def __init__(self):
        # Define SESSION_DIR as an instance attribute
        self.SESSION_DIR = SESSION_DIR
        
        # Create sessions directory if it doesn't exist
        if not os.path.exists(self.SESSION_DIR):
            os.makedirs(self.SESSION_DIR)
    
    def create_session(self, username, otp, user_ip, user_agent):
        """
        Create a new session for a user with generated OTP
        Returns: session_id
        """
        # Generate a unique session ID
        session_id = str(uuid.uuid4())
        
        # Get current timestamp
        timestamp = int(time.time())
        
        # Create session data
        session_data = {
            "username": username,
            "otp": otp,
            "created_at": timestamp,
            "expires_at": timestamp + OTP_EXPIRY,
            "ip_address": user_ip,
            "user_agent": user_agent,
            "validated": False,
            "attempts": 0
        }
        
        # Save session to file
        session_file = os.path.join(self.SESSION_DIR, f"{session_id}.json")
        with open(session_file, "w") as f:
            json.dump(session_data, f)
        
        return session_id
    
    def validate_otp(self, session_id, entered_otp, user_ip):
        """
        Validate the OTP entered by the user
        Returns: (is_valid, message)
        """
        # Check if session exists
        session_file = os.path.join(self.SESSION_DIR, f"{session_id}.json")
        if not os.path.exists(session_file):
            return False, "Invalid session"
        
        # Load session data
        with open(session_file, "r") as f:
            session = json.load(f)
        
        # Check if session is already validated
        if session.get("validated", False):
            return False, "OTP has already been used"
        
        # Check if session has expired
        current_time = int(time.time())
        if current_time > session["expires_at"]:
            return False, "OTP has expired"
        
        # Increment attempt counter
        session["attempts"] += 1
        
        # Check if too many attempts
        if session["attempts"] > 3:
            self.invalidate_session(session_id)
            return False, "Too many incorrect attempts. Please request a new OTP."
        
        # Validate OTP
        if str(entered_otp) == str(session["otp"]):
            # Mark session as validated
            session["validated"] = True
            session["validation_time"] = current_time
            
            # Update session file
            with open(session_file, "w") as f:
                json.dump(session, f)
                
            return True, "OTP validated successfully"
        else:
            # Update session file with attempt count
            with open(session_file, "w") as f:
                json.dump(session, f)
                
            return False, f"Invalid OTP. {3 - session['attempts']} attempts remaining."
    
    def invalidate_session(self, session_id):
        """
        Invalidate a session after successful authentication or due to security concerns
        """
        session_file = os.path.join(self.SESSION_DIR, f"{session_id}.json")
        if os.path.exists(session_file):
            # We could delete the file, but keeping it with an invalid status is better for logging
            with open(session_file, "r") as f:
                session = json.load(f)
            
            session["invalidated"] = True
            session["invalidated_at"] = int(time.time())
            
            with open(session_file, "w") as f:
                json.dump(session, f)
    
    def has_active_session(self, username):
        """
        Check if a user already has an active session
        Returns: (has_active, session_id)
        """
        # Iterate through all session files
        for filename in os.listdir(self.SESSION_DIR):
            if filename.endswith(".json"):
                filepath = os.path.join(self.SESSION_DIR, filename)
                with open(filepath, "r") as f:
                    session = json.load(f)
                
                # Check if session belongs to user and is still valid
                if (session["username"] == username and 
                    not session.get("invalidated", False) and 
                    int(time.time()) <= session["expires_at"]):
                    return True, filename.split(".")[0]
        
        return False, None
    
    def cleanup_expired_sessions(self):
        """
        Remove expired sessions (can be called periodically)
        """
        current_time = int(time.time())
        for filename in os.listdir(self.SESSION_DIR):
            if filename.endswith(".json"):
                filepath = os.path.join(self.SESSION_DIR, filename)
                try:
                    with open(filepath, "r") as f:
                        session = json.load(f)
                    
                    # If session is expired and more than 1 day old, remove it
                    if current_time > session["expires_at"] + 86400:  # 86400 seconds = 1 day
                        os.remove(filepath)
                except (json.JSONDecodeError, KeyError, OSError):
                    # If file is corrupted, remove it
                    try:
                        os.remove(filepath)
                    except OSError:
                        pass