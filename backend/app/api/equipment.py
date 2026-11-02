from fastapi import APIRouter, HTTPException, Query

from app.schemas.equipment import EquipmentOut, ForecastOut, ReadingOut, StatusOut
from app.services import equipment_service

router = APIRouter(prefix="/equipment", tags=["Оборудование"])


def _or_404(value):
    if value is None:
        raise HTTPException(status_code=404, detail="Оборудование не найдено")
    return value


@router.get("", response_model=list[EquipmentOut], summary="Список всех единиц оборудования")
def list_equipment():
    return equipment_service.list_equipment()


@router.get("/{equipment_id}", response_model=EquipmentOut, summary="Информация об одной единице")
def get_equipment(equipment_id: int):
    return _or_404(equipment_service.get_equipment(equipment_id))


@router.get("/{equipment_id}/status", response_model=StatusOut, summary="Текущее состояние")
def get_status(equipment_id: int):
    return _or_404(equipment_service.get_status(equipment_id))


@router.get("/{equipment_id}/history", response_model=list[ReadingOut],
            summary="История показаний датчиков")
def get_history(equipment_id: int,
                from_cycle: int | None = Query(None, ge=0),
                to_cycle: int | None = Query(None, ge=0),
                limit: int = Query(500, ge=1, le=5000)):
    return _or_404(equipment_service.get_history(equipment_id, from_cycle, to_cycle, limit))


@router.get("/{equipment_id}/forecast", response_model=ForecastOut, summary="Прогноз деградации")
def get_forecast(equipment_id: int):
    return _or_404(equipment_service.get_forecast(equipment_id))
