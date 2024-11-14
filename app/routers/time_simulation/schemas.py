from datetime import datetime
from pydantic import BaseModel, PositiveInt


class TimeSimulationRequest(BaseModel):
    days: PositiveInt


class TimeSimulationResponse(BaseModel):
    success: bool
    current_time: datetime
