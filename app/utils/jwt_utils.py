import os
from datetime import datetime, timedelta, timezone
from typing import Any
from pydantic import BaseModel, EmailStr
from jwt import encode, decode
from jwt.exceptions import InvalidTokenError
from app.global_config import ACCESS_TOKEN_EXPIRE_MINUTES


class EncodeData(BaseModel):
    email: EmailStr


SECRET_KEY = os.environ['SECRET_KEY']
ALGORITHM = os.environ['ALGORITHM']


def create_access_token(data: EncodeData, token_expire_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    expire = datetime.now(timezone.utc) + timedelta(token_expire_minutes)
    to_encode = ({"exp": expire, "sub": data})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_payload(token: str) -> EncodeData | None:
    payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    data: EncodeData | None = payload.get("sub")
    return data
