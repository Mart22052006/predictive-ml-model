from sqlalchemy import Connection, select

from app.models.alerts import Alert


def list_alerts(db: Connection, equipment_id: int | None = None, limit: int = 50) -> list[dict]:
    query = select(Alert)
    if equipment_id is not None:
        query = query.where(Alert.equipment_id == equipment_id)
    query = query.order_by(Alert.triggered_at.desc()).limit(limit)

    return [dict(row) for row in db.execute(query).mappings()]
