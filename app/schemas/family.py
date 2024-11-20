from datetime import datetime
from pydantic import BaseModel, ConfigDict


class Family(BaseModel):
    name: str
    registered_at: datetime


class FamilyInDB(Family):
    model_config = ConfigDict(from_attributes=True)
    id: int
