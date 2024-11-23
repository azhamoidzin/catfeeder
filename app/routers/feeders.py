import datetime
from typing import Annotated, Literal

from fastapi import Depends, HTTPException, status, APIRouter, Request

from database import feeder_provider, user_provider
from database.db import get_db, Session
from schemas.login_registration import NewMember
from schemas.feeders import Feeder, FeederType, FeederInDB
from schemas.users import UserInDB
from schemas.exceptions import NOT_ADMIN, USER_DOES_NOT_EXIST, USER_ALREADY_EXISTS
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
    feeder: Feeder,
    current_user: Annotated[UserInDB, Depends(user_provider.get_current_active_user)],
    db: Session = Depends(get_db),
) -> FeederInDB:
    if not current_user.family_admin:
        return NOT_ADMIN

    created_feeder = feeder_provider.create_feeder(feeder, db)
    return created_feeder

