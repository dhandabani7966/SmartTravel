import re
from typing import List, Tuple

def validate_email(email: str) -> bool:
    """Validate email using regex."""
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(email_regex, email.strip()))

def validate_username(username: str) -> Tuple[bool, str]:
    """Validate username rules: 3-20 chars, alphanumeric or underscores."""
    username = username.strip()
    if not (3 <= len(username) <= 20):
        return False, "Username must be between 3 and 20 characters long."
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False, "Username can only contain alphanumeric characters and underscores."
    return True, ""

def check_password_strength(password: str) -> Tuple[int, List[str]]:
    """
    Check password strength.
    Returns:
        score: int (0 to 4) representing strength.
        feedback: List[str] with suggestions for improvements.
    """
    feedback = []
    score = 0

    if len(password) < 8:
        feedback.append("Password must be at least 8 characters long.")
    else:
        score += 1

    if not any(c.isupper() for c in password):
        feedback.append("Add at least one uppercase letter (A-Z).")
    else:
        score += 1

    if not any(c.islower() for c in password):
        feedback.append("Add at least one lowercase letter (a-z).")
    else:
        score += 1

    if not any(c.isdigit() for c in password) and not any(not c.isalnum() for c in password):
        feedback.append("Add at least one number or special character (e.g. !, @, #, $, %).")
    else:
        score += 1

    return score, feedback
