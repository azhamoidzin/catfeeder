from typing import Annotated, Literal
from fastapi import Depends, HTTPException, status, APIRouter, Request
from fastapi.security import OAuth2PasswordRequestForm
from database import user_provider
from database.db import get_db, Session
from schemas.users import UserInDB
from schemas.exceptions import NOT_ADMIN, USER_DOES_NOT_EXIST
from routers.routers_config import RoutesEnum
from utils.password_utils import get_password_hash
from utils.auth_utils import create_access_token, EncodeData, decode_payload, PyJWTError
from utils.email_utils import send_activation_email


router = APIRouter(prefix=f"/{RoutesEnum.USERS}")


@router.get('/{user_id}')
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
