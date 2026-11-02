from fastapi import APIRouter, HTTPException

from app.schemas.equipment import StatusOut
from app.schemas.predict import PredictIn
from app.services import predict_service

router = APIRouter(prefix="/predict", tags=["Прогнозирование"])


@router.post("", response_model=StatusOut, summary="Ручной запрос инференса")
def predict(body: PredictIn):
    result = predict_service.run_prediction(body.equipment_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Оборудование не найдено")
    return result
