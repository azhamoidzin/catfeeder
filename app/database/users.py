from typing import Annotated
from pydantic import BaseModel, EmailStr
from fastapi import Depends, HTTPException, status
from utils.jwt_utils import decode_payload, InvalidTokenError
from utils.password_utils import verify_password
from database.db import fake_users_db
from routers.routers_config import oauth2_scheme


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


class User(BaseModel):
    user_id: int
    email: EmailStr | None = None
    full_name: str | None = None
    disabled: bool | None = None
    family_id: int | None = None
    registration_date: str | None = None


class UserInDB(User):
    hashed_password: str | None = None


class UserUpdate(UserInDB):
    user_id: None = None


class Token(BaseModel):
    access_token: str
    token_type: str


def get_user(email: EmailStr) -> UserInDB | None:
    if email in fake_users_db:
        user_dict = fake_users_db[email]
        return UserInDB(**user_dict)


def authenticate_user(email: EmailStr, password: str):
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


def add_user(user: User) -> bool:
    fake_users_db[user.email] = user.dict()
    return True


def update_user(user_email: EmailStr, update: UserUpdate):
    if user := get_user(user_email):
        user_updated = user.dict() | {k: v for k, v in update.dict().items() if v is not None}
        fake_users_db[str(user_email)] = user_updated
        return user_updated
    return False


def get_last_id():
    return max([u['user_id'] for u in fake_users_db.values()])
