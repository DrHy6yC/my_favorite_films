import hashlib


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def check_password(password, user_password):
    return hash_password(password) == user_password
