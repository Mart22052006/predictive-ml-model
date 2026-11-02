import itertools
from datetime import datetime

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
STATUSES = {"normal", "warning", "critical"}


def _ts(s: str) -> datetime:
    return datetime.fromisoformat(s)


def test_list_equipment():
    r = client.get("/equipment")
    assert r.status_code == 200
    items = r.json()
    assert len(items) > 0
    assert {"id", "name", "type", "unit_number", "current_cycle", "status", "predicted_rul"} <= set(items[0])
    assert all(e["status"] in STATUSES for e in items)


def test_get_equipment_and_404():
    assert client.get("/equipment/1").json()["id"] == 1
    r = client.get("/equipment/9999")
    assert r.status_code == 404 and "9999" in r.json()["detail"]


def test_status_fields_and_ranges():
    s = client.get("/equipment/1/status").json()
    assert {"equipment_id", "status", "current_cycle", "predicted_rul",
            "defect_probability", "residual"} <= set(s)
    assert s["status"] in STATUSES
    assert s["predicted_rul"] >= 0
    assert 0 <= s["defect_probability"] <= 1


def test_status_matches_equipment_list():
    item = client.get("/equipment").json()[0]
    s = client.get(f"/equipment/{item['id']}/status").json()
    assert (s["status"], s["predicted_rul"], s["current_cycle"]) == \
           (item["status"], item["predicted_rul"], item["current_cycle"])


def test_status_404():
    assert client.get("/equipment/9999/status").status_code == 404


def test_history_ascending_with_14_sensors():
    rows = client.get("/equipment/1/history").json()
    cycles = [r["cycle"] for r in rows]
    assert cycles == sorted(cycles) and len(set(cycles)) == len(cycles)
    assert len(rows[0]["sensors"]) == 14
    assert "s1" not in rows[0]["sensors"]  


def test_history_limit_returns_latest():
    current = client.get("/equipment/1").json()["current_cycle"]
    rows = client.get("/equipment/1/history", params={"limit": 5}).json()
    assert len(rows) == 5 and rows[-1]["cycle"] == current


def test_history_period_filter():
    rows = client.get("/equipment/1/history", params={"from_cycle": 10, "to_cycle": 20}).json()
    assert [r["cycle"] for r in rows] == list(range(10, 21))


def test_history_invalid_params():
    assert client.get("/equipment/1/history", params={"from_cycle": 30, "to_cycle": 10}).status_code == 400
    assert client.get("/equipment/1/history", params={"limit": 0}).status_code == 422
    assert client.get("/equipment/1/history", params={"from_cycle": -1}).status_code == 422


def test_history_404():
    assert client.get("/equipment/9999/history").status_code == 404


def test_forecast_shape():
    f = client.get("/equipment/1/forecast").json()
    pts = f["points"]
    assert pts[0]["cycle"] == f["current_cycle"]
    assert [p["cycle"] for p in pts] == list(range(f["current_cycle"], f["current_cycle"] + len(pts)))
    assert pts[-1]["cycle"] == f["predicted_failure_cycle"]


def test_forecast_rul_decreases_and_stays_non_negative():
    pts = client.get("/equipment/1/forecast").json()["points"]
    ruls = [p["rul"] for p in pts]
    assert all(a >= b for a, b in itertools.pairwise(ruls))
    assert all(p["rul"] >= 0 and p["rul_low"] >= 0 for p in pts)


def test_forecast_interval_contains_rul():
    for p in client.get("/equipment/1/forecast").json()["points"]:
        assert p["rul_low"] <= p["rul"] <= p["rul_high"]


def test_forecast_all_equipment_non_negative():
    for e in client.get("/equipment").json():
        pts = client.get(f"/equipment/{e['id']}/forecast").json()["points"]
        assert min(p["rul"] for p in pts) >= 0


def test_forecast_404():
    assert client.get("/equipment/9999/forecast").status_code == 404


def test_alerts_newest_first():
    alerts = client.get("/alerts").json()
    assert len(alerts) > 0
    times = [_ts(a["triggered_at"]) for a in alerts]
    assert times == sorted(times, reverse=True)
    assert all(a["severity"] in {"info", "warning", "critical"} for a in alerts)


def test_alerts_limit():
    assert len(client.get("/alerts", params={"limit": 2}).json()) == 2
    assert client.get("/alerts", params={"limit": 0}).status_code == 422


def test_alerts_by_equipment():
    equipment_id = client.get("/alerts").json()[0]["equipment_id"]
    alerts = client.get(f"/alerts/{equipment_id}").json()
    assert alerts and all(a["equipment_id"] == equipment_id for a in alerts)


def test_alerts_by_unknown_equipment_404():
    assert client.get("/alerts/9999").status_code == 404


def test_predict():
    r = client.post("/predict", json={"equipment_id": 1})
    assert r.status_code == 200 and r.json()["equipment_id"] == 1
    assert client.post("/predict", json={"equipment_id": 9999}).status_code == 404
    assert client.post("/predict", json={"equipment_id": 0}).status_code == 422
