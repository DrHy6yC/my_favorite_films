import time
import jwt
from typing import Dict

from app.config import JWT_ALGORITHM, JWT_SECRET, TOKEN_LIFETIME
from app.model import UserToken


#TODO поправить возвращаемые данные
def token_response(token: str) -> UserToken:
    return {
        "access_token": token
    }


def sign_jwt(user_name: str) -> UserToken:
    expires = time.time() + float(TOKEN_LIFETIME)
    payload = {
        "user_name": user_name,
        "expires": expires
    }
    print(payload)
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token)


def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}
