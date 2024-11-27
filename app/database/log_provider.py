from sqlalchemy import and_, func

from database.db import Session, DLog
from schemas.logs import Log, LogInDB, LogSearch
from global_state import GLOBAL_STATE


def create_log(log: Log, db: Session) -> LogInDB:
    if not log.registered_at:
        log.registered_at = GLOBAL_STATE.get_current_time()
    log_insert = DLog(**log.dict())
    db.add(log_insert)
    db.commit()
    db.refresh(log_insert)
    return log_insert


def get_logs(log_search: LogSearch, db: Session) -> list[LogInDB]:
    filters = []
    if log_search.family_id is not None:
        filters.append(DLog.family_id == log_search.family_id)
    if log_search.feeder_id is not None:
        filters.append(DLog.feeder_id == log_search.feeder_id)
    if log_search.user_id is not None:
        filters.append(DLog.user_id == log_search.user_id)

    logs = db.query(DLog).where(and_(*filters)).all()
    return [LogInDB.model_validate(log) for log in logs]


def get_total_poured(family_id: int, db: Session) -> int:
    result = db.query(func.sum(DLog.meal_poured)).filter(DLog.family_id == family_id).scalar()
    return result
