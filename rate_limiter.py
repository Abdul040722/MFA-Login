# rate_limiter.py
# Modules used: time, collections

import time
from collections import defaultdict

class RateLimiter:
    def __init__(self):
        # Store attempt counters with timestamps
        # Structure: {key: [(timestamp1, count1), (timestamp2, count2), ...]}
        self.attempts = defaultdict(list)
        
        # Default rate limits
        self.login_limit = 5  # 5 attempts
        self.login_window = 300  # in 5 minutes (300 seconds)
        
        self.otp_limit = 3  # 3 attempts
        self.otp_window = 600  # in 10 minutes (600 seconds)
        
        self.email_limit = 3  # 3 email requests
        self.email_window = 1800  # in 30 minutes (1800 seconds)
        
        # Lockout times (in seconds)
        self.short_lockout = 300  # 5 minutes
        self.medium_lockout = 1800  # 30 minutes
        self.long_lockout = 7200  # 2 hours
        
        # Track lockouts
        self.lockouts = {}

    def _clean_old_attempts(self, key, window):
        """Remove attempts older than the window from the tracking list"""
        current_time = time.time()
        self.attempts[key] = [
            (ts, count) for ts, count in self.attempts[key] 
            if current_time - ts < window
        ]

    def _count_attempts(self, key, window):
        """Count total attempts within the time window"""
        self._clean_old_attempts(key, window)
        return sum(count for _, count in self.attempts[key])

    def _record_attempt(self, key):
        """Record a new attempt"""
        current_time = time.time()
        self.attempts[key].append((current_time, 1))

    def check_lockout(self, key):
        """Check if a key is currently locked out"""
        if key in self.lockouts:
            lockout_time, duration = self.lockouts[key]
            if time.time() < lockout_time + duration:
                # Still locked out
                remaining = int(lockout_time + duration - time.time())
                return True, remaining
            else:
                # Lockout expired
                del self.lockouts[key]
        return False, 0

    def apply_lockout(self, key, violations_count):
        """Apply a lockout based on repeated violations"""
        current_time = time.time()
        
        # Determine lockout duration based on number of violations
        if violations_count <= 2:
            duration = self.short_lockout
        elif violations_count <= 5:
            duration = self.medium_lockout
        else:
            duration = self.long_lockout
            
        self.lockouts[key] = (current_time, duration)
        return duration

    def check_rate_limit(self, key, action_type):
        """
        Check if an action exceeds rate limits
        Returns: (is_allowed, message, lockout_duration)
        """
        # First check if already locked out
        is_locked, remaining = self.check_lockout(key)
        if is_locked:
            return False, f"Too many attempts. Please try again in {remaining} seconds.", remaining
        
        # Define limit and window based on action type
        if action_type == "login":
            limit = self.login_limit
            window = self.login_window
        elif action_type == "otp":
            limit = self.otp_limit
            window = self.otp_window
        elif action_type == "email":
            limit = self.email_limit
            window = self.email_window
        else:
            # Default fallback
            limit = 5
            window = 300
        
        # Count attempts in window
        attempt_count = self._count_attempts(key, window)
        
        # Check if limit exceeded
        if attempt_count >= limit:
            # Apply lockout
            violations_key = f"{key}_violations"
            violations = self._count_attempts(violations_key, 86400)  # Track violations in 24 hours
            self._record_attempt(violations_key)
            
            duration = self.apply_lockout(key, violations)
            return False, f"Rate limit exceeded. Try again in {duration} seconds.", duration
        
        # Record this attempt
        self._record_attempt(key)
        return True, "Action allowed", 0