import datetime
from typing import Annotated, Type
from copy import deepcopy

from pydantic import EmailStr
from fastapi import Depends

from database.db import Session, DFeeder, DTag, DSchedule, update, get_db
from schemas.logs import Log, LogInDB
from schemas.exceptions import INVALID_CREDENTIALS, INACTIVE_USER
from utils.auth_utils import decode_payload, InvalidTokenError
from utils.password_utils import verify_password
from routers.routers_config import oauth2_scheme


def create_log(feeder: FeederCreate, db: Session) -> FeederInDB:
    feeder_insert = DFeeder(
        type=feeder.type,
        name=feeder.name,
        user_id=feeder.user_id,
        max_meal=feeder.max_meal,
        configured=False,
    )
    db.add(feeder_insert)
    db.commit()
    db.refresh(feeder_insert)
    return feeder_to_pydantic(feeder_insert)


def get_feeder_by_id(feeder_id: int, db: Session) -> FeederInDB | None:
    feeder = db.query(DFeeder).where(DFeeder.id == feeder_id).first()
    if feeder:
        return feeder_to_pydantic(feeder)


def update_feeder(feeder_id: int, feeder_update: FeederUpdate, db: Session) -> FeederInDB:
    feeder_update_dict = feeder_update.dict()
    feeder_update_dict['configured'] = True
    db.query(DSchedule).filter(DSchedule.feeder_id == feeder_id).delete()
    db.query(DTag).filter(DTag.feeder_id == feeder_id).delete()

    tags = feeder_update_dict.pop('tags', [])
    schedules = feeder_update_dict.pop('schedule', [])
    query = (
        update(DFeeder)
        .where(DFeeder.id == feeder_id)
        .values(**{k: v for k, v in feeder_update_dict.items() if v is not None})
    )
    for schedule in schedules:
        new_schedule = DSchedule(feeder_id=feeder_id, value=schedule)
        db.add(new_schedule)
    for tag in tags:
        new_tag = DTag(feeder_id=feeder_id, value=tag)
        db.add(new_tag)
    db.execute(query)
    db.commit()
    feeder = db.query(DFeeder).where(DFeeder.id == feeder_id).first()
    return feeder_to_pydantic(feeder)
