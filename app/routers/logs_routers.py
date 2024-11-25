import io
from typing import Annotated, Literal

from fastapi import Depends, HTTPException, status, APIRouter, Request
from fastapi.responses import StreamingResponse

from database import feeder_provider, user_provider, log_provider
from database.db import get_db, Session
from schemas.exceptions import NOT_ADMIN, USER_DOES_NOT_EXIST, USER_ALREADY_EXISTS, NOT_FAMILY_MEMBER, \
    FEEDER_DOES_NOT_EXIST, OPERATION_NOT_ALLOWED, FEEDER_NOT_CONFIGURED
from schemas.logs import LogInDB, LogSearch
from schemas.users import UserInDB
from routers.routers_config import RoutesEnum

router = APIRouter(prefix=f"/{RoutesEnum.LOGS}")


@router.get('/', response_model=list[LogInDB])
def get_user_feeders(
    current_user: Annotated[UserInDB, Depends(user_provider.get_current_active_user)],
    family_id: int | None = None,
    feeder_id: int | None = None,
    user_id: int | None = None,
    db: Session = Depends(get_db),
):
    import logging; logging.error((family_id, user_id, feeder_id))
    family_id = family_id or current_user.family_id
    if family_id != current_user.family_id:
        raise OPERATION_NOT_ALLOWED
    if user_id is not None and (user_id != current_user.id and not current_user.family_admin):
        raise NOT_ADMIN
    user_feeder_ids = [feeder.id for feeder in feeder_provider.get_user_feeders(current_user.id, db)]
    if feeder_id is not None and (feeder_id not in user_feeder_ids and not current_user.family_admin):
        raise NOT_ADMIN
    return log_provider.get_logs(LogSearch(family_id=family_id, user_id=user_id, feeder_id=feeder_id), db)
