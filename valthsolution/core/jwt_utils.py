from datetime import timedelta
from django.utils import timezone
import jwt

from .config import (
    ALGORITHM,
    SECRET_KEY
)


def encode_jwt(data: dict, expires_delta: timedelta | None = None):
    try:
        copy_data = data.copy()
        expire = timezone.now() + expires_delta
        copy_data.update({"exp": expire}) 
        return jwt.encode(copy_data, SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        raise e
    

def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception as e:
        raise e
