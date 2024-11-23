from datetime import datetime
from enum import IntEnum
from pydantic import BaseModel, ConfigDict


class FeederType(IntEnum):
    DEFAULT = 0
    SPIRAL = 1


class Feeder(BaseModel):
    type: FeederType = FeederType.DEFAULT
    name: str
    user_id: int
    max_meal: int
    tags: list[str] = None
    schedule: list[str] = None
    current_meal: int | None = None
    portion_meal: int | None = None
    configured: bool = False
    registered_at: datetime


class FeederInDB(Feeder):
    model_config = ConfigDict(from_attributes=True)
    id: int

