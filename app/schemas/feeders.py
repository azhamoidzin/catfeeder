from datetime import datetime
from enum import IntEnum
from pydantic import BaseModel, ConfigDict


class FeederType(IntEnum):
    DEFAULT = 0
    SPIRAL = 1


class FeederCreate(BaseModel):
    type: FeederType
    name: str
    user_id: int
    max_meal: int


class Feeder(FeederCreate):
    tags: list[str] | None = None
    schedule: list[str] | None = None
    portion_meal: int | None = None
    current_meal: int | None = None
    configured: bool = False


class FeederUpdate(BaseModel):
    name: str | None = None
    tags: list[str] = []
    schedule: list[str] = []
    portion_meal: int | None = None


class FeederInDB(Feeder):
    model_config = ConfigDict(from_attributes=True)
    id: int
    registered_at: datetime | None = None

