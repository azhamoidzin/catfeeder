import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from jwt import encode, decode
from jwt.exceptions import InvalidTokenError, PyJWTError

from global_config import ACCESS_TOKEN_EXPIRE_MINUTES
from schemas.auth import EncodeData


InvalidTokenError = InvalidTokenError

SECRET_KEY = os.environ['SECRET_KEY']
ALGORITHM = os.environ['ALGORITHM']


def create_access_token(data: EncodeData, token_expire_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    expire = datetime.now(timezone.utc) + timedelta(token_expire_minutes)
    to_encode = ({"exp": expire, "sub": dict(data)})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_payload(token: str) -> EncodeData | None:
    payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    data: dict | None = payload.get("sub")
    data = EncodeData(**data) if data else None
    return data
