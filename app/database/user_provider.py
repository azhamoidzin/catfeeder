from typing import Annotated

from pydantic import EmailStr
from fastapi import Depends, HTTPException, status

from database.db import get_db, Session, DUser, update
from schemas.users import User, UserInDB, UserUpdate
from utils.auth_utils import decode_payload, InvalidTokenError
from utils.password_utils import verify_password
from routers.routers_config import oauth2_scheme


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_user_by_email(email: EmailStr, db: Session = Depends(get_db)) -> UserInDB | None:
    user = db.query(DUser).where(DUser.email == email).first()
    if user:
        return UserInDB.model_validate(user)


def create_user(user: User, db: Session) -> UserInDB:
    user_insert = DUser(**user.dict())
    db.add(user_insert)
    db.commit()
    db.refresh(user_insert)
    return UserInDB.model_validate(user_insert)


def update_user(user_update: UserUpdate, db: Session = Depends(get_db)):
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


def authenticate_user(email: EmailStr, password: str):
    user = get_user_by_email(email)
    if not user or user.disabled:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = decode_payload(token)
        if payload is None:
            raise credentials_exception
        token_data = payload
    except InvalidTokenError:
        raise credentials_exception
    user = get_user_by_email(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

