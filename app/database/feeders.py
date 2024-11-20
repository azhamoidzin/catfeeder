from enum import IntEnum, unique
from pydantic import BaseModel, EmailStr, PositiveInt
from database.db import fake_feeders_db
from database.db import BaseDB


@unique
class FeederType(IntEnum):
    DEFAULT = 0
    SPINNING = 1


class Feeder(BaseModel):
    type: FeederType = 0
    name: str
    tags: list[str]
    schedules: list[str]
    max_meal: PositiveInt
    current_meal: PositiveInt
    portion_meal: PositiveInt


class FeederInDB(Feeder):
    id: PositiveInt


class FeederUpdate(BaseModel):
    name: str | None = None
    tags: list[str] | None = None
    schedule: list[str] | None = None
    portion_meal: PositiveInt | None = None


class FeederDB(BaseDB):
    def __init__(self):
        super().__init__()

    def get_feeder(self, feeder_id: PositiveInt) -> FeederInDB:
        pass

    def insert_feeder(self, feeder: Feeder) -> FeederInDB:
        pass

    def update_feeder(self, feeder_update: FeederUpdate) -> FeederInDB:
        pass

    def delete_feeder(self, feeder_id: PositiveInt) -> bool:
        pass
