from typing import Annotated

from pydantic import EmailStr
from fastapi import Depends

from database.db import Session, DUser, update, get_db
from schemas.users import User, UserInDB, UserUpdate
from schemas.exceptions import INVALID_CREDENTIALS, INACTIVE_USER
from utils.auth_utils import decode_payload, InvalidTokenError
from utils.password_utils import verify_password
from routers.routers_config import oauth2_scheme


def get_user_by_email(email: EmailStr, db: Session) -> UserInDB | None:
    user = db.query(DUser).where(DUser.email == email).first()
    if user:
        return UserInDB.model_validate(user)


def get_user_by_id(user_id: int, db: Session) -> UserInDB | None:
    user = db.query(DUser).where(DUser.id == user_id).first()
    if user:
        return UserInDB.model_validate(user)


def create_user(user: User, db: Session) -> UserInDB:
    user_insert = DUser(**user.dict())
    db.add(user_insert)
    db.commit()
    db.refresh(user_insert)
    return UserInDB.model_validate(user_insert)


def update_user(user_update: UserUpdate, db: Session):
    user_update_dict = user_update.dict()
    user_id: int = user_update_dict.pop('id')
    query = (
        update(DUser)
        .where(DUser.id == user_id)
        .values(**{k: v for k, v in user_update_dict.items() if v is not None})
    )
    db.execute(query)
    user = db.query(DUser).where(DUser.id == user_id).first()
    db.commit()
    return UserInDB.model_validate(user)


def authenticate_user(email: EmailStr, password: str, db: Session):
    user = get_user_by_email(email, db)
    if not user or user.disabled:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    try:
        payload = decode_payload(token)
        if payload is None:
            raise INVALID_CREDENTIALS
        token_data = payload
    except InvalidTokenError:
        raise INVALID_CREDENTIALS
    user = get_user_by_email(token_data.email, db)
    if user is None:
        raise INVALID_CREDENTIALS
    user.hashed_password = None
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise INACTIVE_USER
    return current_user

