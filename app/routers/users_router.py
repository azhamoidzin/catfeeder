import datetime
from typing import Annotated, Literal

from fastapi import Depends, HTTPException, status, APIRouter, Request

from database import user_provider
from database.db import get_db, Session
from schemas.login_registration import NewMember
from schemas.users import UserInDB, User
from schemas.exceptions import NOT_ADMIN, USER_DOES_NOT_EXIST, USER_ALREADY_EXISTS
from routers.routers_config import RoutesEnum
from utils.auth_utils import create_access_token, EncodeData
from utils.email_utils import send_activation_email


router = APIRouter(prefix=f"/{RoutesEnum.USERS}")


@router.get('/{user_id}', response_model=UserInDB)
async def get_user_by_id(
    user_id: int | Literal['me'],
    current_user: Annotated[UserInDB, Depends(user_provider.get_current_active_user)],
    db: Session = Depends(get_db),
) -> UserInDB:
    if user_id == 'me':
        return current_user
    user_id: int
    if user_id != current_user.id and not current_user.family_admin:
        raise NOT_ADMIN
    user = user_provider.get_user_by_id(user_id, db)
    if not user:
        raise USER_DOES_NOT_EXIST
    return user


@router.put('/', response_model=bool)
async def add_new_user(
    member: NewMember,
    request: Request,
    current_user: Annotated[UserInDB, Depends(user_provider.get_current_active_user)],
    db: Session = Depends(get_db),
) -> bool:
    if user_provider.get_user_by_email(member.email, db):
        raise USER_ALREADY_EXISTS

    new_member = User(
        email=member.email,
        name=member.name,
        disabled=True,
        family_id=current_user.family_id,
        family_admin=False,
    )
    user_provider.create_user(new_member, db)
    token = create_access_token(EncodeData(email=member.email))
    activation_link = f"{request.headers.get('referer')}{RoutesEnum.ACTIVATE}/{token}"
    target_email = member.email
    return send_activation_email(target_email, member.name, activation_link)


@router.get('/', response_model=list[UserInDB])
async def get_family_users(
    current_user: Annotated[UserInDB, Depends(user_provider.get_current_active_user)],
    db: Session = Depends(get_db),
) -> list[UserInDB]:
    users = user_provider.get_users_by_family_id(current_user.family_id, db)
    return users
