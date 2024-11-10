import hashlib


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def check_password(user_hashed_password, password):
    return hash_password(password) == user_hashed_password
