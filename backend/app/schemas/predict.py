from pydantic import BaseModel, Field


class PredictIn(BaseModel):
    equipment_id: int = Field(ge=1)
