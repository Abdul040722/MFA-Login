# otp.py
# Modules used: random, secrets, time

import random
import secrets
import time

# OTP length
OTP_LENGTH = 6
# OTP expiry time in seconds
OTP_EXPIRY = 600  # 10 minutes

def generate_otp():
    """
    Generate a secure OTP using the secrets module
    Returns: a string representation of the OTP
    """
    # Use cryptographically secure random number generation
    if OTP_LENGTH == 6:
        # Generate a 6-digit OTP
        otp_int = secrets.randbelow(900000) + 100000
    else:
        # Generate an OTP of custom length (default fallback to 6)
        otp_int = secrets.randbelow(10 ** OTP_LENGTH - 10 ** (OTP_LENGTH - 1)) + 10 ** (OTP_LENGTH - 1)
    
    # Cast the integer to a string
    otp_str = str(otp_int)
    return otp_str

def get_otp_expiry_time():
    """
    Get the expiry time for an OTP
    Returns: Unix timestamp when the OTP will expire
    """
    return int(time.time()) + OTP_EXPIRY