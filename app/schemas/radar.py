from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Battery(BaseModel):
    last_charge: Optional[datetime] = Field(None, alias="lastCharge")
    battery_capacity: int = Field(..., alias="batteryCapacity")

    class Config:
        populate_by_name = True

class RadarOut(BaseModel):
    battery: Battery
