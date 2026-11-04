from fastapi import APIRouter, Query

from app.core.db import DB
from app.core.errors import NOT_FOUND, equipment_not_found
from app.schemas.alert import AlertOut
from app.services import alert_service, equipment_service

router = APIRouter(prefix="/alerts", tags=["Алерты"])


@router.get("", response_model=list[AlertOut], summary="Список последних алертов")
def list_alerts(db: DB, limit: int = Query(50, ge=1, le=500, description="Максимум записей")):
    return alert_service.list_alerts(db, limit=limit)


@router.get("/{equipment_id}", response_model=list[AlertOut], responses=NOT_FOUND,
            summary="Алерты по конкретному оборудованию")
def alerts_by_equipment(equipment_id: int, db: DB,
                        limit: int = Query(50, ge=1, le=500, description="Максимум записей")):
    if not equipment_service.equipment_exists(db, equipment_id):
        raise equipment_not_found(equipment_id)
    return alert_service.list_alerts(db, equipment_id, limit)
