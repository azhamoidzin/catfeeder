import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Annotated
import io
from fastapi import Depends, FastAPI, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from database import user_provider
from routers.login_registration_router import router as login_registration_router
from routers.users_router import router as users_router
from routers.feeders_router import router as feeders_router
from routers.logs_routers import router as logs_router


logging.basicConfig(level=logging.DEBUG)

app = FastAPI()
for router in [login_registration_router, users_router, feeders_router, logs_router]:
    app.include_router(router)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#
# async def process_feeder(feeder_id):
#     def get_feeder_dict():
#         for user, user_feeders in fake_feeders_db.items():
#             for feeder_id_db, feeder_dict in user_feeders.items():
#                 if feeder_id_db == feeder_id:
#                     return feeder_dict
#     feeder_dict = get_feeder_dict()
#     logging.debug(f"Adding feeder {feeder_dict['feeder_id']} processor")
#     logs.append({
#         'feeder_id': feeder_dict['feeder_id'],
#         'msg': f"Feeder {feeder_dict['name']}[{feeder_dict['feeder_id']}] loaded into system"
#     })
#     while True:
#         feeder_dict = get_feeder_dict()
#         now = get_current_time()
#         current_time_str = now.strftime("%H:%M")
#
#         if current_time_str in feeder_dict['schedule']:
#             logs.append({
#                 'feeder_id': feeder_dict['feeder_id'],
#                 'msg': f"Feeder {feeder_dict['name']}[{feeder_dict['feeder_id']}] fed for {feeder_dict['meal']}"
#             })
#             logging.debug(f"Feeder {feeder_dict['feeder_id']} processed")
#         await asyncio.sleep(20)
#
#
# class Token(BaseModel):
#     access_token: str
#     token_type: str
#
#
# class TokenData(BaseModel):
#     email: str | None = None
#
#
# class User(BaseModel):
#     email: str | None = None
#     full_name: str | None = None
#     disabled: bool | None = None
#     family_id: int | None = None
#
#
# class UserInDB(User):
#     hashed_password: str
#
#
# def validate_status(x: float):
#     assert 0 <= x <= 1, f"{x} is not beetween 0 and 1"
#
#
# FeederStatus = Annotated[float, AfterValidator(validate_status)]
#
#
# class Feeder(BaseModel):
#     name: str
#     tags: list[str]
#     status: FeederStatus | None = 0
#     schedule: list[str]
#     meal: PositiveInt
#
#
# class FeederDB(Feeder):
#     feeder_id: int
#
#
# class FeederUpdate(BaseModel):
#     name: str | None = None
#     tags: list[str] | None = None
#     status: FeederStatus | None = None
#     schedule: list[str] | None = None
#     meal: PositiveInt | None = None
#
#
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
#
# app = FastAPI()
# app.include_router(login_registration_router)
# origins = ["*"]
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
#
# @app.on_event("startup")
# async def app_startup():
#     logging.debug('Creating feeders on startup')
#     for user, user_feeders in fake_feeders_db.items():
#         for feeder_id, feeder_dict in user_feeders.items():
#             asyncio.create_task(process_feeder(feeder_id))
#
#
# @app.get("/users/me/", response_model=User)
# async def read_users_me(
#     current_user: Annotated[User, Depends(user_provider.get_current_active_user)],
# ):
#     return current_user
#
#
# @app.get("/users/me/feeders/", response_model=list[FeederDB])
# async def read_own_feeders(
#     current_user: Annotated[User, Depends(user_provider.get_current_active_user)],
# ):
#     return list(fake_feeders_db[current_user.email].values())
#
#
# @app.get("/users/me/feeders/{feeder_id}", response_model=FeederDB)
# async def read_own_feeder(
#     feeder_id: int,
#     current_user: Annotated[User, Depends(user_provider.get_current_active_user)],
# ):
#     if feeder_id not in fake_feeders_db[current_user.email]:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Feeder not found",
#         )
#     return fake_feeders_db[current_user.email][feeder_id]
#
#
# @app.get("/users/me/feeders/{feeder_id}/schedule")
# async def read_own_feeder(
#     feeder_id: int,
#     current_user: Annotated[User, Depends(user_provider.get_current_active_user)],
# ):
#     if feeder_id not in fake_feeders_db[current_user.email]:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Feeder not found",
#         )
#     feeder = fake_feeders_db[current_user.email][feeder_id]
#     schedule_str = ', '.join(feeder['schedule'])
#     buffer = io.BytesIO(schedule_str.encode('utf-8'))
#
#     # Return a StreamingResponse with the buffer
#     return StreamingResponse(buffer, media_type='application/octet-stream', headers={
#         'Content-Disposition': 'attachment; filename="schedule.catschedule"'
#     })
#
#
# @app.post("/users/me/feeders/", response_model=FeederDB)
# async def create_feeder(
#     feeder: Feeder,
#     current_user: Annotated[User, Depends(user_provider.get_current_active_user)],
#     background_tasks: BackgroundTasks
# ):
#     _id = max(fake_feeders_db[current_user.email].keys()) + 1
#     new_feeder = {'feeder_id': _id, **feeder.dict()}
#     if current_user.email not in fake_feeders_db:
#         fake_feeders_db[current_user.email] = {}
#     fake_feeders_db[current_user.email][new_feeder['feeder_id']] = new_feeder
#     print(new_feeder)
#     logs.append({
#         'feeder_id': new_feeder['feeder_id'],
#         'msg': f"Feeder {new_feeder['name']}[{new_feeder['feeder_id']}] added by {current_user.full_name}"
#     })
#     background_tasks.add_task(process_feeder, new_feeder['feeder_id'])
#     return new_feeder
#
#
# @app.put("/users/me/feeders/{feeder_id}", response_model=FeederDB)
# async def edit_feeder(
#     feeder_id: int,
#     feeder_update: FeederUpdate,
#     current_user: Annotated[User, Depends(user_provider.get_current_active_user)],
# ):
#     if feeder_id not in fake_feeders_db[current_user.email]:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Feeder not found",
#         )
#     feeder_update = {k: v for k, v in feeder_update.dict().items() if v is not None}
#     new_feeder = {**fake_feeders_db[current_user.email][feeder_id], **feeder_update}
#     fake_feeders_db[current_user.email][feeder_id] = new_feeder
#     logs.append({
#         'feeder_id': new_feeder['feeder_id'],
#         'msg': f"Feeder [{new_feeder['feeder_id']}] edited by {current_user.full_name}"
#     })
#     return new_feeder
#
#
# class FamilyMember(BaseModel):
#     id: int
#     name: str
#     registration: str
#
#
# class Family(BaseModel):
#     id: int
#     name: str
#     members: list[FamilyMember]
#     admin: int
#
#
# @app.get("/family", response_model=Family)
# async def get_family(
#     current_user: Annotated[User, Depends(user_provider.get_current_active_user)],
# ):
#
#     family = fake_families_db[current_user.family_id]
#     members = [{
#         'name': user['full_name'],
#         'id': user['user_id'],
#         'registration': user['registration_date']
#     } for user in fake_users_db.values() if user['family_id'] == current_user.family_id]
#     family['members'] = members
#     return family
#
#
#
#
#
#
#
# class Log(BaseModel):
#     feeder_id: int
#     msg: str
#
#
# @app.get("/feeder/{feeder_id}/logs", response_model=list[Log])
# def get_feeder_logs(
#     feeder_id: int,
#     current_user: Annotated[User, Depends(user_provider.get_current_active_user)],
# ):
#     if feeder_id not in fake_feeders_db[current_user.email]:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Feeder not found",
#         )
#     return [log for log in logs if log.get('feeder_id') == feeder_id]
