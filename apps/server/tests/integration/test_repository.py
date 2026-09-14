from smart_classroom_api.infrastructure.database import Database


def payload(mode="AUTO", *, ac_energy=1.25, reason="BOOT"):
    devices = {
        "ac": {
            "state": "ON",
            "override": "AUTO",
            "runtimeSeconds": 60,
            "transitions": 1,
            "reason": reason,
            "estimatedEnergyWh": ac_energy,
        },
        "fan": {
            "state": "OFF",
            "override": "AUTO",
            "runtimeSeconds": 0,
            "transitions": 0,
            "reason": reason,
            "estimatedEnergyWh": 0,
        },
        "lights": {
            "state": "OFF",
            "override": "AUTO",
            "runtimeSeconds": 0,
            "transitions": 0,
            "reason": reason,
            "estimatedEnergyWh": 0,
        },
        "projector": {
            "state": "OFF",
            "override": "AUTO",
            "runtimeSeconds": 0,
            "transitions": 0,
            "reason": reason,
            "estimatedEnergyWh": 0,
        },
    }
    return {
        "deviceId": "classroom-01",
        "uptimeMs": 1000,
        "temperatureC": 28.5,
        "humidityPct": 61.2,
        "illuminanceLux": 90,
        "occupied": True,
        "mode": mode,
        "devices": devices,
        "estimatedEnergyWh": {"total": ac_energy},
        "network": {"mqtt": True},
    }


def test_database_initializes_and_returns_latest_history(tmp_path):
    database = Database(str(tmp_path / "smart_classroom.db"))

    database.save_telemetry(payload())
    latest = database.latest()
    history = database.history()

    assert latest is not None
    assert latest["deviceId"] == "classroom-01"
    assert latest["timestamp"]
    assert history == [
        {
            "timestamp": latest["timestamp"],
            "temperature": 28.5,
            "humidity": 61.2,
            "illuminance": 90.0,
            "occupancy": 1,
            "operating_mode": "AUTO",
        }
    ]


def test_legacy_events_include_each_device_sample_and_control_action(tmp_path):
    database = Database(str(tmp_path / "smart_classroom.db"))

    database.save_telemetry(payload(reason="TEMP_HIGH"))
    database.save_telemetry(payload(reason="TEMP_HIGH"))
    database.log_action("dashboard", "ac", "FORCE_ON", "broker unavailable")

    events = database.events(limit=20)

    assert len([event for event in events if event["type"] == "device"]) == 8
    assert any(
        event["type"] == "control"
        and event["device"] == "ac"
        and event["message"] == "FORCE_ON -> broker unavailable"
        for event in events
    )


def test_energy_summary_uses_latest_device_totals_by_mode(tmp_path):
    database = Database(str(tmp_path / "smart_classroom.db"))

    database.save_telemetry(payload("CONVENTIONAL", ac_energy=10))
    database.save_telemetry(payload("AUTO", ac_energy=4))
    database.save_telemetry(payload("AUTO", ac_energy=6))

    summary = database.energy_summary()

    assert summary["conventionalWh"] == 10
    assert summary["automatedWh"] == 6
    assert summary["savedWh"] == 4
    assert summary["savingRatioPct"] == 40
    assert summary["model"] == "estimated: nominal power x runtime"


def test_clear_removes_runtime_tables(tmp_path):
    database = Database(str(tmp_path / "smart_classroom.db"))
    database.save_telemetry(payload())
    database.log_action("dashboard", None, "RESET ALL", "published")

    database.clear()

    assert database.latest() is None
    assert database.history() == []
    assert database.events() == []
    assert database.energy_summary()["automatedWh"] == 0
