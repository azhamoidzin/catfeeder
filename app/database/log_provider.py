from sqlalchemy import and_

from database.db import Session, DLog
from schemas.logs import Log, LogInDB, LogSearch


def create_log(log: Log, db: Session) -> LogInDB:
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
