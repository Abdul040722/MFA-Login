# security_logger.py
# Modules used: logging, time, os

import logging
import time
import os
from datetime import datetime

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure security logger
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

# Create handler for security logs
security_handler = logging.FileHandler('logs/security.log')
security_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
security_logger.addHandler(security_handler)

# Create handler for authentication attempts
auth_handler = logging.FileHandler('logs/authentication.log')
auth_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
auth_logger = logging.getLogger('authentication')
auth_logger.setLevel(logging.INFO)
auth_logger.addHandler(auth_handler)

def log_login_attempt(username, ip_address, user_agent, status, details=None):
    """
    Log authentication attempts
    """
    log_data = f"LOGIN ATTEMPT - User: {username}, IP: {ip_address}, Status: {status}"
    if user_agent:
        log_data += f", User-Agent: {user_agent}"
    if details:
        log_data += f", Details: {details}"
    
    if status.startswith("FAIL"):
        auth_logger.warning(log_data)
    else:
        auth_logger.info(log_data)

def log_otp_validation(username, session_id, ip_address, status, details=None):
    """
    Log OTP validation attempts
    """
    log_data = f"OTP VALIDATION - User: {username}, Session: {session_id}, IP: {ip_address}, Status: {status}"
    if details:
        log_data += f", Details: {details}"
    
    if status.startswith("FAIL"):
        auth_logger.warning(log_data)
    else:
        auth_logger.info(log_data)

def log_security_event(event_type, username, ip_address, details=None):
    """
    Log general security events
    """
    log_data = f"{event_type} - User: {username}, IP: {ip_address}"
    if details:
        log_data += f", Details: {details}"
    
    security_logger.warning(log_data)

def log_rate_limit_trigger(ip_address, username, action_type, details=None):
    """
    Log when rate limiting is triggered
    """
    log_data = f"RATE LIMIT - IP: {ip_address}, Action: {action_type}"
    if username:
        log_data += f", User: {username}"
    if details:
        log_data += f", Details: {details}"
    
    security_logger.warning(log_data)