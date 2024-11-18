from typing import Annotated
from fastapi import Depends, HTTPException, status, APIRouter, Request
from fastapi.security import OAuth2PasswordRequestForm
from database.users import (
    get_current_active_user, get_user, authenticate_user, Token, update_user, UserUpdate, UserInDB,
    get_last_id, add_user
)
from routers.login_registration.schemas import ActivationData, NewMember
from routers.routers_config import RoutesEnum
from utils.password_utils import get_password_hash
from utils.jwt_utils import create_access_token, EncodeData, decode_payload, PyJWTError
from utils.email_utils import send_activation_email


router = APIRouter()


@router.post(f'/{RoutesEnum.LOGIN}')
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
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
async def create_family_member(
    member: NewMember,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
    request: Request,
):
    if get_user(member.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exist",
        )
    last_id = get_last_id() + 1
    new_member = UserInDB(
        user_id=last_id,
        full_name=member.name,
        email=member.email,
        family_id=current_user.family_id,
        disabled=True,
        registration_date='today',
        hashed_password=None
    )
    add_user(new_member)
    token = create_access_token(EncodeData(email=member.email))
    activation_link = f"{request.headers.get('referer')}{RoutesEnum.ACTIVATE}/{token}"
    target_email = member.email
    return send_activation_email(target_email, activation_link)


@router.post(f"/{RoutesEnum.ACTIVATE}/{{token}}")
def activate_user(token: str, activation_data: ActivationData):
    try:
        payload = decode_payload(token)
        email: str = dict(payload)['email']
    except (PyJWTError, KeyError):
        raise HTTPException(status_code=400, detail="Invalid token")

    user = get_user(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.disabled:
        raise HTTPException(status_code=400, detail="User already activated")

    hashed_password = get_password_hash(activation_data.password)
    user_update = UserUpdate(disabled=True, registration_date='today', hashed_password=hashed_password)
    update_user(user.email, user_update)
    return {"msg": "Account activated successfully"}
