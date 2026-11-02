from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class AlertOut(BaseModel):
    id: int
    equipment_id: int
    cycle: int
    triggered_at: datetime
    severity: Literal["info", "warning", "critical"]
    message: str
