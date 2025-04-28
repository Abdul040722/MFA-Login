// static/script.js
document.addEventListener('DOMContentLoaded', function() {
    console.log("MFA System script loaded!");
    
    // Password visibility toggle
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');
    
    togglePasswordButtons.forEach(button => {
        button.addEventListener('click', function() {
            const passwordField = this.previousElementSibling;
            
            // Toggle password visibility
            if (passwordField.type === 'password') {
                passwordField.type = 'text';
                this.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>';
            } else {
                passwordField.type = 'password';
                this.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>';
            }
        });
    });

    // Form validation
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            let isValid = true;
            
            // Check required fields
            const requiredFields = form.querySelectorAll('[required]');
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    highlightError(field);
                } else {
                    removeError(field);
                }
            });
            
            // Email validation if email field exists
            const emailField = form.querySelector('input[type="email"]');
            if (emailField && emailField.value.trim()) {
                const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailPattern.test(emailField.value)) {
                    isValid = false;
                    highlightError(emailField, 'Please enter a valid email address');
                }
            }
            
            // Password validation if on register page
            const passwordField = form.querySelector('input[type="password"]');
            if (passwordField && form.action.includes('register') && passwordField.value.trim()) {
                if (passwordField.value.length < 8) {
                    isValid = false;
                    highlightError(passwordField, 'Password must be at least 8 characters long');
                }
            }
            
            if (!isValid) {
                event.preventDefault();
            }
        });
    });
    
    function highlightError(element, message) {
        element.classList.add('error-input');
        element.style.borderColor = 'var(--error-border)';
        
        // Create or update error message
        let errorMessage = element.parentNode.querySelector('.error-message');
        if (!errorMessage && message) {
            errorMessage = document.createElement('div');
            errorMessage.className = 'error-message';
            errorMessage.style.color = 'var(--error-text)';
            errorMessage.style.fontSize = '0.8rem';
            errorMessage.style.marginTop = '0.25rem';
            element.parentNode.appendChild(errorMessage);
        }
        
        if (errorMessage && message) {
            errorMessage.textContent = message;
        }
    }
    
    function removeError(element) {
        element.classList.remove('error-input');
        element.style.borderColor = '';
        
        const errorMessage = element.parentNode.querySelector('.error-message');
        if (errorMessage) {
            errorMessage.remove();
        }
    }
    
    // OTP input handling
    const otpDigits = document.querySelectorAll('.otp-digit');
    if (otpDigits.length > 0) {
        const otpField = document.getElementById('otp');
        
        // Allow only numbers in OTP fields
        otpDigits.forEach(digit => {
            digit.addEventListener('input', function(e) {
                this.value = this.value.replace(/[^0-9]/g, '');
                updateOtpValue();
            });
            
            // Handle paste event for OTP
            digit.addEventListener('paste', function(e) {
                e.preventDefault();
                const paste = (e.clipboardData || window.clipboardData).getData('text');
                if (/^\d+$/.test(paste)) {
                    // Fill in all digits from pasted value
                    const digits = paste.split('').slice(0, otpDigits.length);
                    otpDigits.forEach((digit, index) => {
                        if (digits[index]) {
                            digit.value = digits[index];
                        }
                    });
                    updateOtpValue();
                    
                    // Focus the appropriate field
                    if (digits.length < otpDigits.length) {
                        otpDigits[digits.length].focus();
                    } else {
                        otpDigits[otpDigits.length - 1].focus();
                    }
                }
            });
        });
        
        function updateOtpValue() {
            let otp = '';
            otpDigits.forEach(digit => {
                otp += digit.value;
            });
            otpField.value = otp;
        }
    }
    
    // Flash messages auto-dismiss
    const flashMessages = document.querySelectorAll('.messages li');
    if (flashMessages.length > 0) {
        setTimeout(() => {
            flashMessages.forEach(message => {
                message.style.opacity = '0';
                message.style.transition = 'opacity 0.5s ease';
                setTimeout(() => {
                    message.remove();
                }, 500);
            });
        }, 5000);
    }
});