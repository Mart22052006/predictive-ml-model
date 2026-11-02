from fastapi import APIRouter, Query

from app.core.errors import NOT_FOUND, equipment_not_found
from app.schemas.alert import AlertOut
from app.services import alert_service, equipment_service

router = APIRouter(prefix="/alerts", tags=["Алерты"])


@router.get("", response_model=list[AlertOut], summary="Список последних алертов")
def list_alerts(limit: int = Query(50, ge=1, le=500, description="Максимум записей")):
    return alert_service.list_alerts(limit=limit)


@router.get("/{equipment_id}", response_model=list[AlertOut], responses=NOT_FOUND,
            summary="Алерты по конкретному оборудованию")
def alerts_by_equipment(equipment_id: int,
                        limit: int = Query(50, ge=1, le=500, description="Максимум записей")):
    if equipment_service.get_equipment(equipment_id) is None:
        raise equipment_not_found(equipment_id)
    return alert_service.list_alerts(equipment_id, limit)
