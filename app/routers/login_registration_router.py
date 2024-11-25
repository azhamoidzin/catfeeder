import datetime
from typing import Annotated

from fastapi import Depends, HTTPException, status, APIRouter, Request
from fastapi.security import OAuth2PasswordRequestForm

from routers.routers_config import RoutesEnum
from utils.password_utils import get_password_hash
from utils.auth_utils import create_access_token, EncodeData, decode_payload, PyJWTError
from utils.email_utils import send_activation_email
from schemas.login_registration import ActivationData, NewAdminMember
from schemas.users import User, UserUpdate
from schemas.family import Family
from schemas.auth import Token
from schemas.exceptions import USER_ALREADY_EXISTS
from database import user_provider, family_provider
from database.db import get_db, Session

router = APIRouter()


@router.post(f'/{RoutesEnum.LOGIN}')
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> Token:
    user = user_provider.authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data=EncodeData(email=user.email)
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post(f"/{RoutesEnum.REGISTER}")
async def register(
    member: NewAdminMember,
    request: Request,
    db: Session = Depends(get_db),
):
    if user_provider.get_user_by_email(member.email, db):
        raise USER_ALREADY_EXISTS
    family = Family(name=member.family_name)
    family_id = family_provider.create_family(family, db).id
    new_member = User(
        email=member.email,
        name=member.name,
        disabled=True,
        family_id=family_id,
        family_admin=True,
    )
    user_provider.create_user(new_member, db)
    token = create_access_token(EncodeData(email=member.email))
    activation_link = f"{request.headers.get('referer')}{RoutesEnum.ACTIVATE}/{token}"
    target_email = member.email
    return send_activation_email(target_email, member.name, activation_link)


@router.post(f"/{RoutesEnum.ACTIVATE}/{{token}}")
def activate_user(token: str, activation_data: ActivationData, db: Session = Depends(get_db)):
    try:
        payload = decode_payload(token)
        email: str = payload.email
    except (PyJWTError, KeyError):
        raise HTTPException(status_code=422, detail="Invalid token")

    user = user_provider.get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.disabled:
        raise HTTPException(status_code=400, detail="User already activated")

    hashed_password = get_password_hash(activation_data.password)
    user_update = UserUpdate(
        disabled=False,
        hashed_password=hashed_password,
    )
    user_provider.update_user(user.id, user_update, db)
    return {"msg": "Account activated successfully"}
