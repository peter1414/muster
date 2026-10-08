import re

USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,30}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_username(username):
    if not username or not USERNAME_RE.match(username):
        return "Username must be 3-30 characters: letters, numbers, underscore only."
    return None


def validate_email(email):
    if not email or not EMAIL_RE.match(email):
        return "Enter a valid email address."
    return None


def validate_password(password):
    if not password or len(password) < 8:
        return "Password must be at least 8 characters."
    return None
