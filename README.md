## Project Overview

This project is a simple web-based Multi-Factor Authentication (MFA) system using Flask. It includes user registration, login, and OTP (One-Time Password) verification. The project is divided into three main Python scripts:

- `app.py`: Main application handling user login, registration, and OTP verification.
- `auth.py`: Contains the user account management logic, including user creation, password validation, and authentication.
- `otp.py`: Provides the functionality to generate a random one-time password for MFA.

---

## Script Details

### `app.py`

This script is the entry point for the MFA system, using Flask to provide the following functionality:

- **Homepage (`/`)**: Displays the login page.
- **Registration Page (`/register`)**: Allows users to create new accounts by providing a username, email, and password.
- **Login Page (`/login`)**: Handles user login. If the credentials are correct, a one-time password (OTP) is generated and sent for verification.
- **OTP Verification Page (`/otp`)**: Displays a form where users can enter the OTP sent to them for additional security verification.

Flask's `flash()` function is used to display messages to users during registration, login, and OTP verification. The app's secret key is required for session management and message flashing.

**Required Modules**:
- `Flask`: For routing and web interface.
- `auth`: Custom authentication module (handles user creation and login).
- `otp`: Custom OTP generation module.

### `auth.py`

This script handles the user account creation and login functionality. It provides the following:

- **User class**: Defines a user with a username, email, and hashed password. It includes a method to convert user data into a dictionary format for JSON storage.
- **Password Validation (`validate_password`)**: Ensures that the password meets the minimum length and character requirements (uppercase, lowercase, special characters).
- **Password Hashing (`hash_password`)**: Uses SHA-256 hashing to securely store passwords.
- **User Creation (`create_user`)**: Validates the password, hashes it, and stores the user data in a `users.json` file.
- **Credential Check (`check_user_credentials`)**: Verifies a user's credentials during login by comparing the hashed passwords.

**Required Modules**:
- `os`: For file handling (checking if the user data file exists).
- `json`: For reading and writing user data to a JSON file.
- `hashlib`: For securely hashing passwords.

### `otp.py`

This script generates a one-time password (OTP) for multi-factor authentication (MFA). The OTP is a 6-digit number generated randomly.

- **OTP Generation (`generate_otp`)**: Generates a random integer between 100000 and 999999, then casts it to a string to be returned as the OTP.

**Required Modules**:
- `random`: For generating random numbers.

---

## File Structure

```
MFA Login Project/
├── main.py                # Main application entry point (Flask server)
├── auth.py                # Authentication module (User class, registration,login)
├── otp.py                 # OTP generation module (includes casting and functions)
├── data/
│   └── users.json         # File storage for user accounts
├── templates/
│   ├── index.html         # Login page
│   ├── register.html      # User registration page
│   └── otp.html           # OTP verification page
└── static/
    ├── style.css          # CSS for styling
    └── script.js          # JavaScript (for future enhancements)
```
