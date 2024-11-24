import time
import jwt
from typing import Dict

from app.config import JWT_ALGORITHM
from app.model import UserToken


JWT_SECRET: str = JWT_ALGORITHM
JWT_ALGORITHM: str = JWT_ALGORITHM


def token_response(token: str) -> UserToken:
    return {
        "access_token": token
    }


#TODO добавить переменную срока жизни токена
def sign_jwt(user_name: str) -> UserToken:
    payload = {
        "user_name": user_name,
        "expires": time.time() + 600
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token)


def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}
