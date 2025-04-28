# email_service.py
# Modules used: smtplib, email, os, time, logging

import smtplib
import time
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Configure logging
logging.basicConfig(
    filename='logs/email_delivery.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Email configuration
SMTP_SERVER = "mail.smtp2go.com"  # Replace with actual SMTP server
SMTP_PORT = 587
SMTP_USERNAME = "EMAIL"  # Replace with actual email
SMTP_PASSWORD = "PASSWORD"  # Replace with actual password or use environment variables
SENDER_EMAIL = "EMAIL"  # Replace with actual sender email

# Maximum number of retry attempts for email delivery
MAX_RETRIES = 3
# Time to wait between retry attempts (in seconds)
RETRY_INTERVAL = 30

def send_otp_email(recipient_email, otp_code, username):
    """
    Send OTP code via email with retry mechanism
    Returns: (success, message)
    """
    # Create email message
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = recipient_email
    message["Subject"] = "Your MFA Login Verification Code"
    
    # Email body
    body = f"""
    Hello {username},
    
    Your one-time password (OTP) for authentication is: {otp_code}
    
    This code will expire in 10 minutes.
    
    If you did not request this code, please ignore this email and consider changing your password.
    
    Best regards,
    MFA System Security Team
    """
    
    message.attach(MIMEText(body, "plain"))
    
    # Retry mechanism
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # Connect to SMTP server
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            
            # Send email
            server.send_message(message)
            server.quit()
            
            # Log successful delivery
            logging.info(f"OTP email sent successfully to {recipient_email} (attempt {attempt})")
            return True, "OTP sent successfully to your email"
            
        except Exception as e:
            logging.error(f"Failed to send OTP email to {recipient_email} (attempt {attempt}): {str(e)}")
            
            # If we've reached max retries, give up
            if attempt >= MAX_RETRIES:
                logging.error(f"Maximum retry attempts reached for {recipient_email}")
                return False, "Failed to send OTP. Please try again later."
            
            # Wait before retrying
            time.sleep(RETRY_INTERVAL)
    
    # This should not be reached, but just in case
    return False, "Failed to send OTP due to an unexpected error"