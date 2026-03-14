import time

from pydantic import BaseModel, Field, field_validator


class IoTDataCreate(BaseModel):
    user_id: str
    metric_1: float = Field(..., ge=0, le=100)
    metric_2: float = Field(..., ge=0, le=200)
    metric_3: float
    timestamp: int

    @field_validator("timestamp")
    @classmethod
    def timestamp_not_in_future(cls, v: int) -> int:
        if v > int(time.time()):
            raise ValueError("Timestamp cannot be in the future")
        return v


class IoTDataResponse(BaseModel):
    user_id: str
    metric_1: float
    metric_2: float
    metric_3: float
    timestamp: int


class IoTDataBrief(BaseModel):
    metric_1: float
    metric_2: float
    metric_3: float
    timestamp: int
