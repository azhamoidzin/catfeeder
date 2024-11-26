import io
from typing import Annotated, Literal

from fastapi import Depends, HTTPException, status, APIRouter, Request
from fastapi.responses import StreamingResponse

from global_state import GLOBAL_STATE
from database import feeder_provider, user_provider, log_provider
from database.db import get_db, Session
from schemas.exceptions import NOT_ADMIN, USER_DOES_NOT_EXIST, USER_ALREADY_EXISTS, NOT_FAMILY_MEMBER, \
    FEEDER_DOES_NOT_EXIST, OPERATION_NOT_ALLOWED, FEEDER_NOT_CONFIGURED
from schemas.family import FamilyStatusResponse
from schemas.users import UserInDB
from routers.routers_config import RoutesEnum

router = APIRouter(prefix=f"/{RoutesEnum.FAMILY}")


@router.get('/status', response_model=FamilyStatusResponse)
def get_user_feeders(
    current_user: Annotated[UserInDB, Depends(user_provider.get_current_active_user)],
    db: Session = Depends(get_db),
):
    family_id = current_user.family_id
    total_poured = log_provider.get_total_poured(family_id, db)
    users = user_provider.get_users_by_family_id(family_id, db)
    total_users = len(users)
    total_feeders = 0
    for user in users:
        total_feeders += len(feeder_provider.get_user_feeders(user.id, db))
    return FamilyStatusResponse(
        total_users=total_users,
        total_feeders=total_feeders,
        total_poured=total_poured,
        current_time=GLOBAL_STATE.get_current_time(),
    )

