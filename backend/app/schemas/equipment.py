from typing import Literal

from pydantic import BaseModel

Status = Literal["normal", "warning", "critical"]


class EquipmentOut(BaseModel):
    id: int
    name: str
    type: str
    unit_number: int
    current_cycle: int
    status: Status
    predicted_rul: float


class StatusOut(BaseModel):
    equipment_id: int
    status: Status
    current_cycle: int
    predicted_rul: float
    defect_probability: float
    residual: float


class ReadingOut(BaseModel):
    cycle: int
    sensors: dict[str, float]


class ForecastPoint(BaseModel):
    cycle: int
    rul: float
    rul_low: float
    rul_high: float


class ForecastOut(BaseModel):
    equipment_id: int
    current_cycle: int
    predicted_rul: float
    predicted_failure_cycle: int
    points: list[ForecastPoint]
