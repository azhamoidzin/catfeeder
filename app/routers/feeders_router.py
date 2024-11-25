import io
from typing import Annotated, Literal

from fastapi import Depends, HTTPException, status, APIRouter, Request
from fastapi.responses import StreamingResponse

from database import feeder_provider, user_provider
from database.db import get_db, Session
from schemas.login_registration import NewMember
from schemas.feeders import FeederCreate, FeederType, FeederInDB, FeederUpdate
from schemas.users import UserInDB
from schemas.exceptions import NOT_ADMIN, USER_DOES_NOT_EXIST, USER_ALREADY_EXISTS, NOT_FAMILY_MEMBER, \
    FEEDER_DOES_NOT_EXIST, OPERATION_NOT_ALLOWED, FEEDER_NOT_CONFIGURED
from routers.routers_config import RoutesEnum

router = APIRouter(prefix=f"/{RoutesEnum.FEEDERS}")


@router.get('/', response_model=list[FeederInDB])
def get_user_feeders(
    current_user: Annotated[UserInDB, Depends(user_provider.get_current_active_user)],
    db: Session = Depends(get_db),
):
    return feeder_provider.get_user_feeders(current_user.id, db)


@router.put('/', response_model=FeederInDB)
async def add_new_feeder(
    feeder: FeederCreate,
    current_user: Annotated[UserInDB, Depends(user_provider.get_current_active_user)],
    db: Session = Depends(get_db),
) -> FeederInDB:
    if not current_user.family_admin:
        return NOT_ADMIN
    # if current_user.id == feeder.user_id:
    #     raise OPERATION_NOT_ALLOWED
    user = user_provider.get_user_by_id(feeder.user_id, db)
    if not user or user.family_id != current_user.family_id:
        raise NOT_FAMILY_MEMBER
    created_feeder = feeder_provider.create_feeder(feeder, db)
    return created_feeder


@router.post('/{feeder_id}', response_model=FeederInDB)
async def add_new_feeder(
    feeder_id: int,
    feeder_update: FeederUpdate,
    current_user: Annotated[UserInDB, Depends(user_provider.get_current_active_user)],
    db: Session = Depends(get_db),
) -> FeederInDB:
    feeder = feeder_provider.get_feeder_by_id(feeder_id, db)
    if not feeder:
        raise FEEDER_DOES_NOT_EXIST
    if feeder.user_id != current_user.id and not current_user.family_admin:
        raise OPERATION_NOT_ALLOWED
    feeder_db = feeder_provider.update_feeder(feeder_id, feeder_update, db)
    return feeder_db


@router.get("/{feeder_id}/schedule")
async def download_schedule(
    feeder_id: int,
    current_user: Annotated[UserInDB, Depends(user_provider.get_current_active_user)],
    db: Session = Depends(get_db),
):
    feeder = feeder_provider.get_feeder_by_id(feeder_id, db)
    if not feeder:
        raise FEEDER_DOES_NOT_EXIST
    if not feeder.configured:
        raise FEEDER_NOT_CONFIGURED
    schedule_str = ', '.join(feeder.schedule)
    buffer = io.BytesIO(schedule_str.encode('utf-8'))

    return StreamingResponse(buffer, media_type='application/octet-stream', headers={
        'Content-Disposition': 'attachment; filename="schedule.catschedule"'
    })

