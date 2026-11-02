from app.services.mock_data import ALERTS


def list_alerts(equipment_id: int | None = None, limit: int = 50) -> list[dict]:
    items = [a for a in ALERTS if equipment_id is None or a["equipment_id"] == equipment_id]
    return items[:limit]
