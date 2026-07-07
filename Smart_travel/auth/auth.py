import bcrypt
import os
from typing import Any, Dict, Tuple, Optional
from database.db import execute, fetch_one, log_audit
from utils.logger import get_logger, log_exception

logger = get_logger("auth")

# Default admin variables loaded from env or default values
DEFAULT_ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@smarttravel.local")
DEFAULT_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Admin@123")

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def check_password(password: str, hashed: str) -> bool:
    """Check password against hash using bcrypt."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception as exc:
        log_exception(logger, "Password checking exception", exc)
        return False

def register_user(username: str, email: str, password: str, is_admin: bool = False) -> Tuple[bool, str]:
    """Register a new user in the database."""
    username = username.strip()
    email = email.strip().lower()
    
    # Check duplicate username
    dup_user = fetch_one("SELECT id FROM users WHERE username = ?", (username,))
    if dup_user:
        logger.warning(f"Registration failed: Username '{username}' already exists.")
        return False, f"Username '{username}' is already taken."
        
    # Check duplicate email
    dup_email = fetch_one("SELECT id FROM users WHERE email = ?", (email,))
    if dup_email:
        logger.warning(f"Registration failed: Email '{email}' already exists.")
        return False, "An account with this email is already registered."
        
    try:
        hashed = hash_password(password)
        admin_flag = 1 if is_admin else 0
        user_id = execute(
            "INSERT INTO users (username, email, password_hash, is_admin) VALUES (?, ?, ?, ?)",
            (username, email, hashed, admin_flag)
        )
        
        log_audit(user_id, "user_registration", f"User {username} successfully registered.")
        logger.info(f"User '{username}' registered with ID {user_id}.")
        return True, "Registration successful! You can now log in."
    except Exception as exc:
        log_exception(logger, f"Registration failed for '{username}'", exc)
        return False, "An internal error occurred. Please try again later."

def authenticate_user(email_or_username: str, password: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """Authenticate user with email or username and password."""
    val = email_or_username.strip()
    
    # Find user by email or username
    user = fetch_one(
        "SELECT id, username, email, password_hash, is_admin, created_at FROM users WHERE email = ? OR username = ?",
        (val.lower(), val)
    )
    
    if not user:
        logger.warning(f"Authentication failed: User '{val}' not found.")
        return False, None, "Invalid username/email or password."
        
    if check_password(password, user["password_hash"]):
        user_data = {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "is_admin": bool(user["is_admin"]),
            "created_at": user["created_at"]
        }
        log_audit(user["id"], "user_login", f"User {user['username']} logged in successfully.")
        logger.info(f"User '{user['username']}' authenticated successfully.")
        return True, user_data, "Login successful."
    else:
        log_audit(user["id"], "user_login_failed", f"Failed login attempt for user {user['username']}.")
        logger.warning(f"Authentication failed: Incorrect password for user '{user['username']}'.")
        return False, None, "Invalid username/email or password."

def update_user_password(user_id: int, current_password: str, new_password: str) -> Tuple[bool, str]:
    """Update user's password."""
    user = fetch_one("SELECT username, password_hash FROM users WHERE id = ?", (user_id,))
    if not user:
        return False, "User not found."
        
    if not check_password(current_password, user["password_hash"]):
        return False, "Current password is incorrect."
        
    try:
        new_hash = hash_password(new_password)
        execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
        log_audit(user_id, "password_change", f"User {user['username']} changed password.")
        logger.info(f"Password updated successfully for user ID {user_id}.")
        return True, "Password updated successfully."
    except Exception as exc:
        log_exception(logger, f"Password update failed for user ID {user_id}", exc)
        return False, "An error occurred updating password."

def ensure_default_admin() -> None:
    """Ensure that the default administrator account exists."""
    try:
        admin = fetch_one("SELECT id FROM users WHERE email = ?", (DEFAULT_ADMIN_EMAIL,))
        if not admin:
            logger.info("Default admin not found. Creating default admin account...")
            success, msg = register_user(
                username=DEFAULT_ADMIN_USERNAME,
                email=DEFAULT_ADMIN_EMAIL,
                password=DEFAULT_ADMIN_PASSWORD,
                is_admin=True
            )
            if success:
                logger.info(f"Default admin account '{DEFAULT_ADMIN_USERNAME}' created successfully.")
            else:
                logger.error(f"Failed to create default admin: {msg}")
        else:
            logger.info("Default admin account already exists.")
    except Exception as exc:
        log_exception(logger, "Error ensuring default admin", exc)
