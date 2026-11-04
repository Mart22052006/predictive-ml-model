from sqlalchemy import Connection

from app.services import equipment_service


def run_prediction(db: Connection, equipment_id: int) -> dict | None:
    return equipment_service.get_status(db, equipment_id)
