from datetime import datetime
from pydantic import BaseModel, ConfigDict


class LogSearch(BaseModel):
    family_id: int | None = None
    feeder_id: int | None = None
    user_id: int | None = None


class Log(LogSearch):
    log: str
    meal_poured: int | None = 0


class LogInDB(Log):
    model_config = ConfigDict(from_attributes=True)
    id: int
    registered_at: datetime
