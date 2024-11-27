import logging
from typing import Annotated, Literal

from fastapi import Depends, HTTPException, status, APIRouter, Request, BackgroundTasks

from database import feeder_provider, user_provider, log_provider
from database.db import get_db, Session
from schemas.users import UserInDB
from schemas.time_simulation import TimeSimulationRequest
from schemas.exceptions import NOT_ADMIN, USER_DOES_NOT_EXIST, USER_ALREADY_EXISTS, NOT_FAMILY_MEMBER, \
    FEEDER_DOES_NOT_EXIST, OPERATION_NOT_ALLOWED, FEEDER_NOT_CONFIGURED
from routers.routers_config import RoutesEnum
from global_state import GLOBAL_STATE, timedelta


router = APIRouter(prefix=f"/{RoutesEnum.TIME_SIMULATION}")


@router.post('/travel')
async def warp(
    body: TimeSimulationRequest,
    current_user: Annotated[UserInDB, Depends(user_provider.get_current_active_user)],
    db: Session = Depends(get_db),
):
    feeders = feeder_provider._get_all_feeders(db)
    start_date = GLOBAL_STATE.get_current_time()
    end_date = start_date + timedelta(days=body.days)
    current_date = start_date
    while current_date < end_date:
        current_time_str = current_date.strftime("%H:%M")
        for feeder in feeders:
            if current_time_str in feeder.schedule:

                success, amount = feeder_provider.perform_feed(feeder.id, db)
                how = feeder.type.feed_type_str()
                log_provider.create_log(log_provider.Log(
                    log=f"Scheduled activation ({how}) "
                        f"feeder [{feeder.id}] ({feeder.name}) by {amount} (Success: {success})! #TIMETRAVEL",
                    family_id=user_provider.get_user_by_id(feeder.user_id, db).family_id,
                    user_id=None,
                    feeder_id=feeder.id,
                    meal_poured=amount,
                    registered_at=current_date,
                ), db)
        current_date += timedelta(seconds=60)
    async with GLOBAL_STATE.time_lock:
        GLOBAL_STATE.time_offset += timedelta(days=body.days)

