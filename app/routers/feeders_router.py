import io
from typing import Annotated, Literal

from fastapi import Depends, HTTPException, status, APIRouter, Request
from fastapi.responses import StreamingResponse

from database import feeder_provider, user_provider, log_provider
from database.db import get_db, Session
from schemas.login_registration import NewMember
from schemas.feeders import FeederCreate, FeederType, FeederInDB, FeederUpdate, InstantFeedResponse
from schemas.users import UserInDB
from schemas.exceptions import NOT_ADMIN, USER_DOES_NOT_EXIST, USER_ALREADY_EXISTS, NOT_FAMILY_MEMBER, \
    FEEDER_DOES_NOT_EXIST, OPERATION_NOT_ALLOWED, FEEDER_NOT_CONFIGURED
from routers.routers_config import RoutesEnum

router = APIRouter(prefix=f"/{RoutesEnum.FEEDERS}")


@router.get('/', response_model=list[FeederInDB])
def get_user_feeders(
    current_user: Annotated[UserInDB, Depends(user_provider.get_current_active_user)],
    user_id: int | None = None,
    db: Session = Depends(get_db),
):
    if not user_id:
        if not current_user.family_admin:
            raise NOT_ADMIN
        user_id = [user.id for user in user_provider.get_users_by_family_id(current_user.family_id, db)]
    return feeder_provider.get_user_feeders(user_id, db)


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
    log_provider.create_log(log_provider.Log(
        log=f"User [{current_user.id}] ({current_user.name}) registered "
            f"feeder [{created_feeder.id}] ({created_feeder.name}) for "
            f"user [{user.id}] ({user.name})!",
        family_id=user.family_id,
        user_id=current_user.id,
        feeder_id=created_feeder.id,
    ), db)
    return created_feeder


@router.post('/{feeder_id}', response_model=FeederInDB)
async def add_new_feeder(
    feeder_id: int,
    feeder_update: FeederUpdate,
    current_user: Annotated[UserInDB, Depends(user_provider.get_current_active_user)],
    db: Session = Depends(get_db),
) -> FeederInDB:
    feeder = feeder_provider.get_feeder_by_id(feeder_id, db)
    if feeder.user_id != current_user.id and not current_user.family_admin:
        raise OPERATION_NOT_ALLOWED
    feeder_db = feeder_provider.update_feeder(feeder_id, feeder_update, db)
    log_provider.create_log(log_provider.Log(
        log=f"User [{current_user.id}] ({current_user.name}) updated "
            f"feeder [{feeder_db.id}] ({feeder_db.name})!",
        family_id=current_user.family_id,
        user_id=feeder_db.user_id,
        feeder_id=feeder_db.id,
    ), db)
    return feeder_db


@router.get("/{feeder_id}/schedule")
async def download_schedule(
    feeder_id: int,
    current_user: Annotated[UserInDB, Depends(user_provider.get_current_active_user)],
    db: Session = Depends(get_db),
):
    feeder = feeder_provider.get_feeder_by_id(feeder_id, db)
    if not feeder.configured:
        raise FEEDER_NOT_CONFIGURED
    if feeder.user_id != current_user.id and not current_user.family_admin:
        raise OPERATION_NOT_ALLOWED
    schedule_str = ', '.join(feeder.schedule)
    buffer = io.BytesIO(schedule_str.encode('utf-8'))
    return StreamingResponse(buffer, media_type='application/octet-stream', headers={
        'Content-Disposition': 'attachment; filename="schedule.catschedule"'
    })


@router.post("/{feeder_id}/instant_feed")
async def download_schedule(
    feeder_id: int,
    current_user: Annotated[UserInDB, Depends(user_provider.get_current_active_user)],
    db: Session = Depends(get_db),
):
    feeder = feeder_provider.get_feeder_by_id(feeder_id, db)
    if not feeder.configured:
        raise FEEDER_NOT_CONFIGURED
    if feeder.user_id != current_user.id and not current_user.family_admin:
        raise OPERATION_NOT_ALLOWED
    success, amount = feeder_provider.perform_feed(feeder_id, db)
    how = feeder.type.feed_type_str()
    log_provider.create_log(log_provider.Log(
        log=f"User [{current_user.id}] ({current_user.name}) activated ({how}) "
            f"feeder [{feeder.id}] ({feeder.name}) by {amount} (Success: {success})!",
        family_id=current_user.family_id,
        user_id=current_user.id,
        feeder_id=feeder.id,
        meal_poured=amount,
    ), db)
    return InstantFeedResponse(fed=success, amount=amount)
