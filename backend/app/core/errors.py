from fastapi import HTTPException


def equipment_not_found(equipment_id: int) -> HTTPException:
    return HTTPException(status_code=404, detail=f"Оборудование с id={equipment_id} не найдено")


NOT_FOUND = {404: {"description": "Оборудование не найдено"}}
