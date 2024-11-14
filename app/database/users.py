from typing import Annotated
from pydantic import BaseModel, EmailStr
from fastapi import Depends, HTTPException, status
from app.utils.jwt_utils import decode_payload, InvalidTokenError
from app.utils.password_utils import verify_password
from app.database.db import fake_users_db
from app.routers.routers_config import oauth2_scheme


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


class User(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    disabled: bool | None = None
    family_id: int | None = None


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


def get_user(email: str):
    if email in fake_users_db:
        user_dict = fake_users_db[email]
        return UserInDB(**user_dict)


def authenticate_user(email: str, password: str):
    user = get_user(email)
    if not user or user.disabled:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = decode_payload(token)
        if payload is None:
            raise credentials_exception
        token_data = payload
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
