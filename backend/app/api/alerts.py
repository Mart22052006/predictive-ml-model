from fastapi import APIRouter, HTTPException, Query

from app.schemas.alert import AlertOut
from app.services import alert_service, equipment_service

router = APIRouter(prefix="/alerts", tags=["Алерты"])


@router.get("", response_model=list[AlertOut], summary="Список последних алертов")
def list_alerts(limit: int = Query(50, ge=1, le=500)):
    return alert_service.list_alerts(limit=limit)


@router.get("/{equipment_id}", response_model=list[AlertOut], summary="Алерты по оборудованию")
def alerts_by_equipment(equipment_id: int, limit: int = Query(50, ge=1, le=500)):
    if equipment_service.get_equipment(equipment_id) is None:
        raise HTTPException(status_code=404, detail="Оборудование не найдено")
    return alert_service.list_alerts(equipment_id, limit)
