from typing import Type
from copy import deepcopy

from database.db import Session, DFeeder, DTag, DSchedule, update, get_db
from schemas.feeders import FeederType, FeederInDB, FeederCreate, FeederUpdate
from schemas.exceptions import FEEDER_DOES_NOT_EXIST


def feeder_to_pydantic(feeder: Type[DFeeder] | DFeeder | None) -> FeederInDB | None:
    if not feeder:
        return None
    feeder_dict = deepcopy(feeder.__dict__)
    feeder_dict['tags'] = [tag.value for tag in feeder.tags]
    feeder_dict['schedule'] = [sch.value for sch in feeder.schedule]
    return FeederInDB.model_validate(feeder_dict)


def get_user_feeders(user_id: int | list[int], db: Session) -> list[FeederInDB]:
    if isinstance(user_id, int):
        user_id: list[int] = [user_id]
    feeders = db.query(DFeeder).where(DFeeder.user_id.in_(user_id)).all()
    return [feeder_to_pydantic(feeder) for feeder in feeders]


def create_feeder(feeder: FeederCreate, db: Session) -> FeederInDB:
    feeder_insert = DFeeder(
        type=feeder.type,
        name=feeder.name,
        user_id=feeder.user_id,
        max_meal=feeder.max_meal,
        current_meal=0,
        configured=False,
    )
    db.add(feeder_insert)
    db.commit()
    db.refresh(feeder_insert)
    return feeder_to_pydantic(feeder_insert)


def get_feeder_by_id(feeder_id: int, db: Session) -> FeederInDB:
    feeder = db.query(DFeeder).where(DFeeder.id == feeder_id).first()
    feeder = feeder_to_pydantic(feeder)
    if feeder:
        return feeder
    raise FEEDER_DOES_NOT_EXIST


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


def perform_feed(feeder_id: int, db: Session) -> (bool, int):
    feeder = db.query(DFeeder).where(DFeeder.id == feeder_id).first()
    if not feeder:
        raise FEEDER_DOES_NOT_EXIST
    if feeder.current_meal < feeder.portion_meal:
        return False, 0
    feeder.current_meal -= feeder.portion_meal
    db.commit()
    db.refresh(feeder)
    return True, feeder.portion_meal


def perform_refill(feeder_id: int, db: Session) -> bool:
    feeder = db.query(DFeeder).where(DFeeder.id == feeder_id).first()
    if not feeder:
        raise FEEDER_DOES_NOT_EXIST
    feeder.current_meal = feeder.max_meal
    db.commit()
    db.refresh(feeder)
    return True
