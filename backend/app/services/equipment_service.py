import math

from app.services.mock_data import EQUIPMENT, READINGS


def list_equipment() -> list[dict]:
    return list(EQUIPMENT.values())


def get_equipment(equipment_id: int) -> dict | None:
    return EQUIPMENT.get(equipment_id)


def get_status(equipment_id: int) -> dict | None:
    e = EQUIPMENT.get(equipment_id)
    if e is None:
        return None
    rul = e["predicted_rul"]
    return {
        "equipment_id": equipment_id, "status": e["status"], "current_cycle": e["current_cycle"],
        "predicted_rul": rul, "residual": e["residual"],
        "defect_probability": round(1 / (1 + math.exp((rul - 50) / 12)), 3),
    }


def get_history(equipment_id: int, from_cycle: int | None, to_cycle: int | None,
                limit: int) -> list[dict] | None:
    if equipment_id not in EQUIPMENT:
        return None
    rows = [r for r in READINGS[equipment_id]
            if (from_cycle is None or r["cycle"] >= from_cycle)
            and (to_cycle is None or r["cycle"] <= to_cycle)]
    return rows[-limit:]


def get_forecast(equipment_id: int) -> dict | None:
    e = EQUIPMENT.get(equipment_id)
    if e is None:
        return None
    rul, cycle = e["predicted_rul"], e["current_cycle"]
    horizon = round(rul)
    points = []
    for k in range(horizon + 1):
        value, spread = rul - k, 2 + 0.12 * k
        points.append({"cycle": cycle + k, "rul": round(value, 1),
                       "rul_low": round(max(0.0, value - spread), 1), "rul_high": round(value + spread, 1)})
    return {"equipment_id": equipment_id, "current_cycle": cycle, "predicted_rul": rul,
            "predicted_failure_cycle": cycle + horizon, "points": points}
