from datetime import datetime
from pydantic import BaseModel, ConfigDict


class Family(BaseModel):
    name: str


class FamilyInDB(Family):
    model_config = ConfigDict(from_attributes=True)
    id: int
    registered_at: datetime


class FamilyStatusResponse(BaseModel):
    total_users: int
    total_feeders: int
    total_poured: int
    current_time: datetime
