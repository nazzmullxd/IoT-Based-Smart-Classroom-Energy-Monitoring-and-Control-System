import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from .energy import energy_wh, saving_percentage


SCHEMA = """
CREATE TABLE IF NOT EXISTS telemetry(
    id INTEGER PRIMARY KEY,
    timestamp TEXT NOT NULL,
    received_at TEXT NOT NULL DEFAULT '',
    device_id TEXT NOT NULL DEFAULT 'classroom-01',
    boot_id TEXT,
    sequence INTEGER,
    mode TEXT NOT NULL DEFAULT 'SMART',
    occupancy INTEGER NOT NULL DEFAULT 0,
    temperature_c REAL,
    humidity_pct REAL,
    lux REAL NOT NULL DEFAULT 0,
    light_state INTEGER NOT NULL DEFAULT 0,
    fan_state INTEGER NOT NULL DEFAULT 0,
    cooling_state INTEGER NOT NULL DEFAULT 0,
    light_runtime_seconds REAL NOT NULL DEFAULT 0,
    fan_runtime_seconds REAL NOT NULL DEFAULT 0,
    cooling_runtime_seconds REAL NOT NULL DEFAULT 0,
    light_interval_seconds REAL NOT NULL DEFAULT 0,
    fan_interval_seconds REAL NOT NULL DEFAULT 0,
    cooling_interval_seconds REAL NOT NULL DEFAULT 0,
    light_energy_wh REAL NOT NULL DEFAULT 0,
    fan_energy_wh REAL NOT NULL DEFAULT 0,
    cooling_energy_wh REAL NOT NULL DEFAULT 0,
    estimated_energy_wh REAL NOT NULL DEFAULT 0,
    switching_events INTEGER NOT NULL DEFAULT 0,
    sensor_error INTEGER NOT NULL DEFAULT 0
);
"""


REQUIRED_COLUMNS = {
    "received_at": "TEXT NOT NULL DEFAULT ''",
    "device_id": "TEXT NOT NULL DEFAULT 'classroom-01'",
    "boot_id": "TEXT",
    "sequence": "INTEGER",
    "mode": "TEXT NOT NULL DEFAULT 'SMART'",
    "temperature_c": "REAL",
    "humidity_pct": "REAL",
    "lux": "REAL NOT NULL DEFAULT 0",
    "light_state": "INTEGER NOT NULL DEFAULT 0",
    "fan_state": "INTEGER NOT NULL DEFAULT 0",
    "cooling_state": "INTEGER NOT NULL DEFAULT 0",
    "light_runtime_seconds": "REAL NOT NULL DEFAULT 0",
    "fan_runtime_seconds": "REAL NOT NULL DEFAULT 0",
    "cooling_runtime_seconds": "REAL NOT NULL DEFAULT 0",
    "light_interval_seconds": "REAL NOT NULL DEFAULT 0",
    "fan_interval_seconds": "REAL NOT NULL DEFAULT 0",
    "cooling_interval_seconds": "REAL NOT NULL DEFAULT 0",
    "light_energy_wh": "REAL NOT NULL DEFAULT 0",
    "fan_energy_wh": "REAL NOT NULL DEFAULT 0",
    "cooling_energy_wh": "REAL NOT NULL DEFAULT 0",
    "estimated_energy_wh": "REAL NOT NULL DEFAULT 0",
    "switching_events": "INTEGER NOT NULL DEFAULT 0",
    "sensor_error": "INTEGER NOT NULL DEFAULT 0",
}


class Database:
    def __init__(self, path: str | Path, powers: dict[str, float]):
        self.path = Path(path)
        self.powers = powers
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript(SCHEMA)
            self._upgrade_legacy_table(db)
            db.execute(
                "CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp ON telemetry(timestamp)"
            )
            db.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_mode ON telemetry(mode)")

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            yield db
            db.commit()
        finally:
            db.close()

    @staticmethod
    def _upgrade_legacy_table(db: sqlite3.Connection) -> None:
        existing = {row["name"] for row in db.execute("PRAGMA table_info(telemetry)")}
        for name, definition in REQUIRED_COLUMNS.items():
            if name not in existing:
                db.execute(f"ALTER TABLE telemetry ADD COLUMN {name} {definition}")

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def save(self, data: dict) -> bool:
        received_at = self._now()
        timestamp = data.get("timestamp") or received_at
        if hasattr(timestamp, "isoformat"):
            timestamp = timestamp.isoformat()
        devices = ("light", "fan", "cooling")

        with self.connect() as db:
            previous = db.execute(
                "SELECT * FROM telemetry ORDER BY id DESC LIMIT 1"
            ).fetchone()
            intervals: dict[str, float] = {}
            for device in devices:
                current = float(data.get(f"{device}_runtime_seconds", 0))
                if previous is None:
                    interval = 0.0
                elif data.get("boot_id") and previous["boot_id"] == data.get("boot_id"):
                    interval = max(0.0, current - previous[f"{device}_runtime_seconds"])
                else:
                    interval = current
                intervals[device] = interval

            energy = {
                device: energy_wh(self.powers[device], intervals[device])
                for device in devices
            }
            switching = sum(
                int(data.get(f"{device}_switching_events", 0)) for device in devices
            )
            columns = {
                "timestamp": str(timestamp),
                "received_at": received_at,
                "device_id": data.get("device_id", "classroom-01"),
                "boot_id": data.get("boot_id"),
                "sequence": data.get("sequence"),
                "mode": data.get("mode", "SMART"),
                "occupancy": int(data.get("occupancy", False)),
                "temperature_c": data.get("temperature_c"),
                "humidity_pct": data.get("humidity_pct"),
                "lux": data.get("lux", 0),
                "light_state": int(data.get("light", False)),
                "fan_state": int(data.get("fan", False)),
                "cooling_state": int(data.get("cooling", False)),
                "light_runtime_seconds": data.get("light_runtime_seconds", 0),
                "fan_runtime_seconds": data.get("fan_runtime_seconds", 0),
                "cooling_runtime_seconds": data.get("cooling_runtime_seconds", 0),
                "light_interval_seconds": intervals["light"],
                "fan_interval_seconds": intervals["fan"],
                "cooling_interval_seconds": intervals["cooling"],
                "light_energy_wh": energy["light"],
                "fan_energy_wh": energy["fan"],
                "cooling_energy_wh": energy["cooling"],
                "estimated_energy_wh": sum(energy.values()),
                "switching_events": switching,
                "sensor_error": int(data.get("sensor_error", False)),
            }

            # Old databases may retain mandatory legacy columns. Supplying them
            # preserves existing local data without keeping legacy code paths.
            table_columns = {
                row["name"] for row in db.execute("PRAGMA table_info(telemetry)")
            }
            legacy = {
                "operating_mode": columns["mode"],
                "temperature": columns["temperature_c"],
                "humidity": columns["humidity_pct"],
                "illuminance": columns["lux"],
                "payload": "{}",
            }
            columns.update({key: value for key, value in legacy.items() if key in table_columns})
            names = ", ".join(columns)
            placeholders = ", ".join("?" for _ in columns)
            db.execute(
                f"INSERT INTO telemetry({names}) VALUES({placeholders})",
                tuple(columns.values()),
            )
        return True

    @staticmethod
    def _row(row: sqlite3.Row) -> dict:
        return {
            "id": row["id"],
            "timestamp": row["timestamp"],
            "mode": row["mode"],
            "occupancy": bool(row["occupancy"]),
            "temperature_c": row["temperature_c"],
            "humidity_pct": row["humidity_pct"],
            "lux": row["lux"],
            "light": bool(row["light_state"]),
            "fan": bool(row["fan_state"]),
            "cooling": bool(row["cooling_state"]),
            "light_runtime_seconds": row["light_runtime_seconds"],
            "fan_runtime_seconds": row["fan_runtime_seconds"],
            "cooling_runtime_seconds": row["cooling_runtime_seconds"],
            "estimated_energy_wh": row["estimated_energy_wh"],
            "switching_events": row["switching_events"],
            "sensor_error": bool(row["sensor_error"]),
            "device_id": row["device_id"],
            "boot_id": row["boot_id"],
            "sequence": row["sequence"],
        }

    def latest(self) -> dict | None:
        with self.connect() as db:
            row = db.execute("SELECT * FROM telemetry ORDER BY id DESC LIMIT 1").fetchone()
        return self._row(row) if row else None

    def history(self, limit: int = 100) -> list[dict]:
        with self.connect() as db:
            rows = db.execute(
                "SELECT * FROM telemetry ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [self._row(row) for row in reversed(rows)]

    def energy_summary(self) -> dict:
        with self.connect() as db:
            rows = db.execute(
                """
                SELECT mode,
                       SUM(light_energy_wh) light_wh,
                       SUM(fan_energy_wh) fan_wh,
                       SUM(cooling_energy_wh) cooling_wh,
                       SUM(estimated_energy_wh) total_wh
                FROM telemetry
                WHERE mode IN ('SMART', 'CONVENTIONAL')
                GROUP BY mode
                """
            ).fetchall()
        modes = {
            "SMART": {"light_wh": 0.0, "fan_wh": 0.0, "cooling_wh": 0.0, "total_wh": 0.0},
            "CONVENTIONAL": {"light_wh": 0.0, "fan_wh": 0.0, "cooling_wh": 0.0, "total_wh": 0.0},
        }
        for row in rows:
            modes[row["mode"]] = {
                "light_wh": row["light_wh"] or 0.0,
                "fan_wh": row["fan_wh"] or 0.0,
                "cooling_wh": row["cooling_wh"] or 0.0,
                "total_wh": row["total_wh"] or 0.0,
            }
        smart = modes["SMART"]["total_wh"]
        conventional = modes["CONVENTIONAL"]["total_wh"]
        return {
            "energy_type": "ESTIMATED",
            "model": "nominal power (W) x runtime (h)",
            "smart": modes["SMART"],
            "conventional": modes["CONVENTIONAL"],
            "estimated_saving_wh": conventional - smart,
            "estimated_saving_pct": saving_percentage(conventional, smart),
        }

    def clear(self) -> None:
        with self.connect() as db:
            db.execute("DELETE FROM telemetry")
