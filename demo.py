from datetime import datetime, timedelta, timezone
from typing import Annotated
import io
import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel, PositiveInt, AfterValidator

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2a$10$KSEpyXKj/a0KuV/z8eutQOpE9J6juwowmJO83fUzUp.u3oFdFP8GK",
        "disabled": False,
    }
}

fake_feeders_db = {
    'johndoe': {
        228: {
            'feeder_id': 228,
            'name': 'Kitchen',
            'tags': ['tag1'],
            'status': 0.5,
            'schedule': ['09:00', '12:00', '15:00', '18:00', '21:00'],
            'meal': 25
        },
        337: {
            'feeder_id': 337,
            'name': 'MainCoon OGROMNYI',
            'tags': ['tag3', 'tag5'],
            'status': 0.0,
            'schedule': ['09:30', '12:30', '15:30', '18:30', '18:41', '21:30'],
            'meal': 1000
        }
    }
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
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
    return list(fake_feeders_db[current_user.username].values())


@app.get("/users/me/feeders/{feeder_id}", response_model=FeederDB)
async def read_own_feeder(
    feeder_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    if feeder_id not in fake_feeders_db[current_user.username]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feeder not found",
        )
    return fake_feeders_db[current_user.username][feeder_id]


@app.get("/users/me/feeders/{feeder_id}/schedule")
async def read_own_feeder(
    feeder_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    if feeder_id not in fake_feeders_db[current_user.username]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feeder not found",
        )
    feeder = fake_feeders_db[current_user.username][feeder_id]
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
):
    _id = max(fake_feeders_db[current_user.username].keys()) + 1
    new_feeder = {'feeder_id': _id, **feeder.dict()}
    fake_feeders_db[current_user.username][new_feeder['feeder_id']] = new_feeder
    print(new_feeder)
    return new_feeder


@app.put("/users/me/feeders/{feeder_id}", response_model=FeederDB)
async def read_own_feeders(
    feeder_id: int,
    feeder_update: FeederUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    if feeder_id not in fake_feeders_db[current_user.username]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feeder not found",
        )
    feeder_update = {k: v for k, v in feeder_update.dict().items() if v is not None}
    new_feeder = {**fake_feeders_db[current_user.username][feeder_id], **feeder_update}
    fake_feeders_db[current_user.username][feeder_id] = new_feeder
    return new_feeder
