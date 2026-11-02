import random
from datetime import UTC, datetime, timedelta, timezone

from app.core.config import RUL_CLIP, RUL_CRITICAL, RUL_WARNING

SENSORS = {
    "s2": (641.82, 0.50, 1), "s3": (1589.70, 6.13, 1), "s4": (1400.60, 9.00, 1),
    "s7": (554.36, 0.89, -1), "s8": (2388.06, 0.07, 1), "s9": (9046.19, 22.08, 1),
    "s11": (47.47, 0.27, 1), "s12": (521.66, 0.74, -1), "s13": (2388.02, 0.07, 1),
    "s14": (8138.62, 19.08, 1), "s15": (8.4195, 0.04, 1), "s17": (392.0, 1.55, 1),
    "s20": (39.06, 0.18, -1), "s21": (23.419, 0.11, -1),
}

_rnd = random.Random(42)

EQUIPMENT: dict[int, dict] = {}
READINGS: dict[int, list[dict]] = {}
ALERTS: list[dict] = []


def status_from_rul(rul: float) -> str:
    if rul <= RUL_CRITICAL:
        return "critical"
    if rul <= RUL_WARNING:
        return "warning"
    return "normal"


def noisy_rul(true_rul: float) -> float:
    return round(min(max(min(true_rul, RUL_CLIP) + _rnd.gauss(0, 4), 0), RUL_CLIP), 1)


def _build() -> None:
    now = datetime.now(UTC)
    for i in range(1, 13):
        life = _rnd.randint(130, 300)                  
        cut = int(life * _rnd.uniform(0.35, 0.97))    
        READINGS[i] = [
            {"cycle": c, "sensors": {
                code: round(base + trend * std * 3 * (c / life) ** 2 + _rnd.gauss(0, std * 0.4), 4)
                for code, (base, std, trend) in SENSORS.items()}}
            for c in range(1, cut + 1)
        ]
        predicted = noisy_rul(life - cut)
        EQUIPMENT[i] = {
            "id": i, "name": f"ТРДД-{i:03d}", "type": "Турбовентиляторный двигатель",
            "unit_number": i, "current_cycle": cut, "predicted_rul": predicted,
            "status": status_from_rul(predicted), "residual": round(_rnd.gauss(0, 0.5), 3),
            "true_rul": life - cut,
        }
        for threshold, severity, text in (
            (RUL_WARNING, "warning", "Остаточный ресурс ниже 75 циклов — запланируйте обслуживание"),
            (RUL_CRITICAL, "critical", "Остаточный ресурс ниже 30 циклов — требуется срочная проверка"),
        ):
            if life - threshold <= cut:
                ALERTS.append({"id": len(ALERTS) + 1, "equipment_id": i, "cycle": life - threshold,
                               "triggered_at": now - timedelta(seconds=30 * (cut - (life - threshold))),
                               "severity": severity, "message": text})
    ALERTS.sort(key=lambda a: a["triggered_at"], reverse=True)


_build()
