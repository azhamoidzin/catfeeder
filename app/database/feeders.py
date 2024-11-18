from pydantic import BaseModel, EmailStr, PositiveInt
from database.db import fake_feeders_db


class Feeder(BaseModel):
    name: str
    tags: list[str]
    status: float | None = 0
    schedule: list[str]
    meal: PositiveInt


class FeederDB(Feeder):
    feeder_id: int


class FeederUpdate(BaseModel):
    name: str | None = None
    tags: list[str] | None = None
    status: float | None = None
    schedule: list[str] | None = None
    meal: PositiveInt | None = None


def get_user_feeders(email: EmailStr) -> list[FeederDB]:
    return list(fake_feeders_db[email].values())


def get_feeder_by_id(feeder_id: PositiveInt) -> FeederDB | None:
    if feeder := list(filter(lambda user_feeders: feeder_id in user_feeders.keys(), fake_feeders_db.values())):
        return feeder[0]
    return None


def add_feeder(feeder: Feeder) -> FeederDB:
    pass


def update_feeder_by_id(feeder_id: int) -> FeederDB:
    pass
