from app.services import equipment_service
from app.services.mock_data import EQUIPMENT, noisy_rul, status_from_rul


def run_prediction(equipment_id: int) -> dict | None:
    e = EQUIPMENT.get(equipment_id)
    if e is None:
        return None
    e["predicted_rul"] = noisy_rul(e["true_rul"])
    e["status"] = status_from_rul(e["predicted_rul"])
    return equipment_service.get_status(equipment_id)
