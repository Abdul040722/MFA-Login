# otp.py
# This module generates a one-time password (OTP) for multi-factor authentication.
# It uses functions, casting, and standard modules to create a simple OTP.
# Modules used: random

import random  # For generating random numbers

# Function to generate a 6-digit OTP
def generate_otp():
    # Generate a random integer between 100000 and 999999
    otp_int = random.randint(100000, 999999)
    # CAST the integer to a string (casting requirement)
    otp_str = str(otp_int)
    return otp_str
