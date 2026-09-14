from fastapi.testclient import TestClient

from smart_classroom_api.config import Settings
from smart_classroom_api.database import Database
from smart_classroom_api.main import create_app


POWERS = {"light": 120.0, "fan": 75.0, "cooling": 1500.0}


def payload(sequence=1, mode="SMART", runtime=0):
    return {
        "device_id": "classroom-01",
        "boot_id": "test-boot",
        "sequence": sequence,
        "uptime_ms": sequence * 3000,
        "occupancy": True,
        "temperature_c": 29.5,
        "humidity_pct": 60,
        "lux": 120,
        "light": True,
        "fan": True,
        "cooling": True,
        "mode": mode,
        "light_runtime_seconds": runtime,
        "fan_runtime_seconds": runtime,
        "cooling_runtime_seconds": runtime,
        "light_switching_events": 1,
        "fan_switching_events": 1,
        "cooling_switching_events": 1,
        "estimated_energy_wh": 0,
    }


class FakeMqtt:
    connected = True

    def __init__(self):
        self.commands = []

    def start(self):
        pass

    def stop(self):
        pass

    def publish_mode(self, mode):
        self.commands.append(("mode", mode))
        return True

    def publish_control(self, device, state):
        self.commands.append((device, state))
        return True


def app_for(tmp_path, mqtt=None):
    settings = Settings(
        database_path=tmp_path / "smart_classroom.db",
        dashboard_path=tmp_path,
        mqtt_enabled=False,
    )
    (tmp_path / "index.html").write_text("dashboard", encoding="utf-8")
    return create_app(settings, mqtt_service=mqtt or FakeMqtt())


def test_status_handles_missing_latest_data(tmp_path):
    with TestClient(app_for(tmp_path)) as client:
        response = client.get("/api/status")
        assert response.status_code == 200
        assert response.json()["available"] is False
        assert response.json()["latest"] is None


def test_telemetry_history_and_interval_energy(tmp_path):
    with TestClient(app_for(tmp_path)) as client:
        assert client.post("/api/telemetry", json=payload(1, runtime=0)).json() == {"stored": True}
        assert client.post("/api/telemetry", json=payload(2, runtime=3600)).json() == {"stored": True}
        latest = client.get("/api/status").json()["latest"]
        assert latest["cooling"] is True
        assert len(client.get("/api/history").json()) == 2
        energy = client.get("/api/energy").json()
        assert energy["energy_type"] == "ESTIMATED"
        assert energy["smart"]["total_wh"] == 1695


def test_mode_and_manual_control_use_simple_topics(tmp_path):
    mqtt = FakeMqtt()
    with TestClient(app_for(tmp_path, mqtt)) as client:
        assert client.post("/api/mode", json={"mode": "MANUAL"}).json()["accepted"]
        assert client.post("/api/control", json={"device": "fan", "state": True}).json()["accepted"]
    assert mqtt.commands == [("mode", "MANUAL"), ("fan", True)]


def test_database_preserves_and_returns_research_fields(tmp_path):
    database = Database(tmp_path / "data.db", POWERS)
    database.save(payload())
    assert database.latest()["mode"] == "SMART"
    assert database.latest()["temperature_c"] == 29.5
