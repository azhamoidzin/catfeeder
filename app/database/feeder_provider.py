import datetime
from typing import Annotated

from pydantic import EmailStr
from fastapi import Depends

from database.db import Session, DFeeder, DTag, DSchedule, update, get_db
from schemas.feeders import FeederType, FeederInDB, Feeder
from schemas.exceptions import INVALID_CREDENTIALS, INACTIVE_USER
from utils.auth_utils import decode_payload, InvalidTokenError
from utils.password_utils import verify_password
from routers.routers_config import oauth2_scheme


def get_user_feeders(user_id: int, db: Session) -> list[FeederInDB] | None:
    feeders = db.query(DFeeder).where(DFeeder.user_id == user_id).all()
    if feeders:
        return [FeederInDB.model_validate(feeder) for feeder in feeders]


def create_feeder(feeder: Feeder, db: Session) -> FeederInDB:
    feeder_insert = DFeeder(
        type=feeder.type,
        name=feeder.name,
        user_id=feeder.user_id,
        max_meal=feeder.max_meal,
        configured=False,
        registered_at=datetime.datetime.now(),
    )
    feeder_insert.tags = [DTag(value=tag for tag in feeder.tags)]
    feeder_insert.schedules = [DSchedule(value=sch for sch in feeder.schedule)]
    db.add(feeder_insert)
    db.commit()
    db.refresh(feeder_insert)
    return FeederInDB.model_validate(feeder_insert)

