import importlib, os
from fastapi.testclient import TestClient


def payload(mode="AUTO"):
    devices = {
        n: {
            "state": "OFF",
            "override": "AUTO",
            "runtimeSeconds": 0,
            "transitions": 0,
            "reason": "BOOT",
            "estimatedEnergyWh": 0,
        }
        for n in ("ac", "fan", "lights", "projector")
    }
    return {
        "deviceId": "test",
        "uptimeMs": 1,
        "temperatureC": 28,
        "humidityPct": 60,
        "illuminanceLux": 100,
        "occupied": True,
        "mode": mode,
        "devices": devices,
        "estimatedEnergyWh": {"total": 0},
        "network": {},
    }


def test_api_round_trip(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("MQTT_ENABLED", "false")
    import smart_classroom_api.main as module

    module = importlib.reload(module)
    with TestClient(module.app) as client:
        assert client.get("/api/status").status_code == 200
        assert client.get("/api/telemetry/latest").status_code == 404
        assert client.post("/api/telemetry", json=payload()).json() == {"stored": True}
        assert client.get("/api/telemetry/latest").json()["occupied"] is True
        assert len(client.get("/api/telemetry/history").json()) == 1
        assert client.get("/api/energy").json()["savingRatioPct"] == 0
        assert (
            client.post("/api/control/ac", json={"value": "FORCE_ON"}).status_code
            == 200
        )
        assert (
            client.post("/api/control/unknown", json={"value": "AUTO"}).status_code
            == 404
        )
        assert (
            client.post("/api/mode", json={"mode": "CONVENTIONAL"}).status_code == 200
        )
        assert client.get("/").status_code == 200
