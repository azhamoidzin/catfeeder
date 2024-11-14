import os
from typing import Annotated
import smtplib
from email.mime.text import MIMEText
from pydantic import BaseModel, EmailStr
from fastapi import Depends, HTTPException, status, APIRouter, Request
from fastapi.security import OAuth2PasswordRequestForm
from database.users import (
    get_current_active_user, get_user, authenticate_user, Token, update_user, UserUpdate, UserInDB,
    get_last_id, add_user
)
from routers.routers_config import RoutesEnum
from utils.password_utils import get_password_hash
from utils.jwt_utils import create_access_token, EncodeData, decode_payload, PyJWTError


router = APIRouter()

EMAIL_ADDRESS = os.environ['EMAIL_ADDRESS']
EMAIL_PASSWORD = os.environ['EMAIL_PASSWORD']


class ActivationData(BaseModel):
    password: str


class NewMember(BaseModel):
    name: str
    email: EmailStr


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
    target_email = member.email
    activation_link = f"{request.headers.get('referer')}{RoutesEnum.ACTIVATE}/{token}"
    msg = MIMEText(f"Click the link to activate your account: {activation_link}")
    msg["Subject"] = "Activate your account"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = target_email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, [target_email], msg.as_string())
        return True


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
