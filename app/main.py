import asyncio
import logging
import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from typing import Annotated
import io
import jwt
from fastapi import Depends, FastAPI, HTTPException, status, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from jwt.exceptions import InvalidTokenError, PyJWTError
from passlib.context import CryptContext
from pydantic import BaseModel, PositiveInt, AfterValidator, EmailStr
import os
from database.db import fake_families_db, fake_users_db, fake_feeders_db, logs
from utils.jwt_utils import create_access_token, EncodeData, decode_payload
from database.users import get_current_active_user, authenticate_user
from utils.password_utils import get_password_hash

EMAIL_ADDRESS = os.environ['EMAIL_ADDRESS']
EMAIL_PASSWORD = os.environ['EMAIL_PASSWORD']


# to get a string like this run:
# openssl rand -hex 32


logging.basicConfig(level=logging.DEBUG)

def get_current_time():
    return datetime.now()


async def process_feeder(feeder_id):
    def get_feeder_dict():
        for user, user_feeders in fake_feeders_db.items():
            for feeder_id_db, feeder_dict in user_feeders.items():
                if feeder_id_db == feeder_id:
                    return feeder_dict
    feeder_dict = get_feeder_dict()
    logging.debug(f"Adding feeder {feeder_dict['feeder_id']} processor")
    logs.append({
        'feeder_id': feeder_dict['feeder_id'],
        'msg': f"Feeder {feeder_dict['name']}[{feeder_dict['feeder_id']}] loaded into system"
    })
    while True:
        feeder_dict = get_feeder_dict()
        now = get_current_time()
        current_time_str = now.strftime("%H:%M")

        if current_time_str in feeder_dict['schedule']:
            logs.append({
                'feeder_id': feeder_dict['feeder_id'],
                'msg': f"Feeder {feeder_dict['name']}[{feeder_dict['feeder_id']}] fed for {feeder_dict['meal']}"
            })
            logging.debug(f"Feeder {feeder_dict['feeder_id']} processed")
        await asyncio.sleep(20)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None


class User(BaseModel):
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None
    family_id: int | None = None


class UserInDB(User):
    hashed_password: str


def validate_status(x: float):
    assert 0 <= x <= 1, f"{x} is not beetween 0 and 1"


FeederStatus = Annotated[float, AfterValidator(validate_status)]


class Feeder(BaseModel):
    name: str
    tags: list[str]
    status: FeederStatus | None = 0
    schedule: list[str]
    meal: PositiveInt


class FeederDB(Feeder):
    feeder_id: int


class FeederUpdate(BaseModel):
    name: str | None = None
    tags: list[str] | None = None
    status: FeederStatus | None = None
    schedule: list[str] | None = None
    meal: PositiveInt | None = None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def app_startup():
    logging.debug('Creating feeders on startup')
    for user, user_feeders in fake_feeders_db.items():
        for feeder_id, feeder_dict in user_feeders.items():
            asyncio.create_task(process_feeder(feeder_id))


@app.post("/login")
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


@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@app.get("/users/me/feeders/", response_model=list[FeederDB])
async def read_own_feeders(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return list(fake_feeders_db[current_user.email].values())


@app.get("/users/me/feeders/{feeder_id}", response_model=FeederDB)
async def read_own_feeder(
    feeder_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    if feeder_id not in fake_feeders_db[current_user.email]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feeder not found",
        )
    return fake_feeders_db[current_user.email][feeder_id]


@app.get("/users/me/feeders/{feeder_id}/schedule")
async def read_own_feeder(
    feeder_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    if feeder_id not in fake_feeders_db[current_user.email]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feeder not found",
        )
    feeder = fake_feeders_db[current_user.email][feeder_id]
    schedule_str = ', '.join(feeder['schedule'])
    buffer = io.BytesIO(schedule_str.encode('utf-8'))

    # Return a StreamingResponse with the buffer
    return StreamingResponse(buffer, media_type='application/octet-stream', headers={
        'Content-Disposition': 'attachment; filename="schedule.catschedule"'
    })


@app.post("/users/me/feeders/", response_model=FeederDB)
async def create_feeder(
    feeder: Feeder,
    current_user: Annotated[User, Depends(get_current_active_user)],
    background_tasks: BackgroundTasks
):
    _id = max(fake_feeders_db[current_user.email].keys()) + 1
    new_feeder = {'feeder_id': _id, **feeder.dict()}
    if current_user.email not in fake_feeders_db:
        fake_feeders_db[current_user.email] = {}
    fake_feeders_db[current_user.email][new_feeder['feeder_id']] = new_feeder
    print(new_feeder)
    logs.append({
        'feeder_id': new_feeder['feeder_id'],
        'msg': f"Feeder {new_feeder['name']}[{new_feeder['feeder_id']}] added by {current_user.full_name}"
    })
    background_tasks.add_task(process_feeder, new_feeder['feeder_id'])
    return new_feeder


@app.put("/users/me/feeders/{feeder_id}", response_model=FeederDB)
async def edit_feeder(
    feeder_id: int,
    feeder_update: FeederUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    if feeder_id not in fake_feeders_db[current_user.email]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feeder not found",
        )
    feeder_update = {k: v for k, v in feeder_update.dict().items() if v is not None}
    new_feeder = {**fake_feeders_db[current_user.email][feeder_id], **feeder_update}
    fake_feeders_db[current_user.email][feeder_id] = new_feeder
    logs.append({
        'feeder_id': new_feeder['feeder_id'],
        'msg': f"Feeder [{new_feeder['feeder_id']}] edited by {current_user.full_name}"
    })
    return new_feeder


fake_families_db = {
    0: {
        'id': 0,
        'name': 'SUPER FAMILY',
        'admin': 0,
    }
}

class FamilyMember(BaseModel):
    id: int
    name: str
    registration: str


class Family(BaseModel):
    id: int
    name: str
    members: list[FamilyMember]
    admin: int


@app.get("/family", response_model=Family)
async def get_family(
    current_user: Annotated[User, Depends(get_current_active_user)],
):

    family = fake_families_db[current_user.family_id]
    members = [{
        'name': user['full_name'],
        'id': user['user_id'],
        'registration': user['registration_date']
    } for user in fake_users_db.values() if user['family_id'] == current_user.family_id]
    family['members'] = members
    return family


class NewMember(BaseModel):
    name: str
    email: EmailStr


@app.post("/family")
async def create_family_member(
    member: NewMember,
    current_user: Annotated[User, Depends(get_current_active_user)],
    request: Request,
):
    if len(list(filter(lambda x: x['email'] == member.email, fake_users_db.values()))):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exist",
        )
    last_id = max([u['user_id'] for u in fake_users_db.values()]) + 1
    fake_users_db[member.email] = {
        'user_id': last_id,
        'full_name': member.name,
        'email': member.email,
        'family_id': current_user.family_id, 'disabled': 1
    }
    token = create_access_token(EncodeData(email=member.email))
    target_email = member.email
    activation_link = f"{request.headers.get('referer')}activate/{token}"
    msg = MIMEText(f"Click the link to activate your account: {activation_link}")
    msg["Subject"] = "Activate your account"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = target_email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, [target_email], msg.as_string())
        return True


class ActivationData(BaseModel):
    password: str


@app.post("/activate/{token}")
def activate_user(token: str, activation_data: ActivationData):
    print(fake_users_db)
    try:
        payload = decode_payload(token)
        email: str = dict(payload)['email']
    except (PyJWTError, KeyError):
        raise HTTPException(status_code=400, detail="Invalid token")

    if email not in fake_users_db:
        raise HTTPException(status_code=404, detail="User not found")

    if not fake_users_db[email]['disabled']:
        raise HTTPException(status_code=400, detail="User already activated")

    fake_users_db[email]['disabled'] = 1
    fake_users_db[email]['registration_date'] = 'today'
    fake_users_db[email]['hashed_password'] = get_password_hash(activation_data.password)
    return {"msg": "Account activated successfully"}


class Log(BaseModel):
    feeder_id: int
    msg: str


@app.get("/feeder/{feeder_id}/logs", response_model=list[Log])
def get_feeder_logs(
    feeder_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    if feeder_id not in fake_feeders_db[current_user.email]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feeder not found",
        )
    return [log for log in logs if log.get('feeder_id') == feeder_id]
