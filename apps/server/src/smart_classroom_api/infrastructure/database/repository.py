import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS telemetry(
    id INTEGER PRIMARY KEY,
    timestamp TEXT NOT NULL,
    temperature REAL,
    humidity REAL,
    illuminance REAL,
    occupancy INTEGER NOT NULL,
    operating_mode TEXT NOT NULL,
    payload TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS device_state(
    id INTEGER PRIMARY KEY,
    timestamp TEXT NOT NULL,
    device TEXT NOT NULL,
    state TEXT NOT NULL,
    override_mode TEXT NOT NULL,
    reason TEXT
);
CREATE TABLE IF NOT EXISTS energy(
    id INTEGER PRIMARY KEY,
    timestamp TEXT NOT NULL,
    device TEXT NOT NULL,
    runtime_seconds REAL NOT NULL,
    estimated_energy_wh REAL NOT NULL,
    operating_mode TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS control_action(
    id INTEGER PRIMARY KEY,
    timestamp TEXT NOT NULL,
    source TEXT NOT NULL,
    device TEXT,
    command TEXT NOT NULL,
    result TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_telemetry_time ON telemetry(timestamp);
CREATE INDEX IF NOT EXISTS idx_device_time ON device_state(timestamp);
CREATE INDEX IF NOT EXISTS idx_energy_time ON energy(timestamp);
CREATE INDEX IF NOT EXISTS idx_action_time ON control_action(timestamp);
"""


class Database:
    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript(SCHEMA)

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
    def now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def save_telemetry(self, data: dict) -> None:
        ts = self.now()
        with self.connect() as db:
            db.execute(
                """
                INSERT INTO telemetry(
                    timestamp,
                    temperature,
                    humidity,
                    illuminance,
                    occupancy,
                    operating_mode,
                    payload
                )
                VALUES(?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ts,
                    data.get("temperatureC"),
                    data.get("humidityPct"),
                    data.get("illuminanceLux", 0),
                    int(data.get("occupied", False)),
                    data.get("mode", "AUTO"),
                    json.dumps(data),
                ),
            )
            for name, item in data.get("devices", {}).items():
                db.execute(
                    """
                    INSERT INTO device_state(
                        timestamp,
                        device,
                        state,
                        override_mode,
                        reason
                    )
                    VALUES(?, ?, ?, ?, ?)
                    """,
                    (
                        ts,
                        name,
                        item.get("state", "OFF"),
                        item.get("override", "AUTO"),
                        item.get("reason"),
                    ),
                )
                db.execute(
                    """
                    INSERT INTO energy(
                        timestamp,
                        device,
                        runtime_seconds,
                        estimated_energy_wh,
                        operating_mode
                    )
                    VALUES(?, ?, ?, ?, ?)
                    """,
                    (
                        ts,
                        name,
                        item.get("runtimeSeconds", 0),
                        item.get("estimatedEnergyWh", 0),
                        data.get("mode", "AUTO"),
                    ),
                )

    def latest(self) -> dict | None:
        with self.connect() as db:
            row = db.execute(
                "SELECT payload, timestamp FROM telemetry ORDER BY id DESC LIMIT 1"
            ).fetchone()
        if not row:
            return None
        value = json.loads(row["payload"])
        value["timestamp"] = row["timestamp"]
        return value

    def history(self, limit: int = 200) -> list[dict]:
        with self.connect() as db:
            rows = db.execute(
                """
                SELECT
                    timestamp,
                    temperature,
                    humidity,
                    illuminance,
                    occupancy,
                    operating_mode
                FROM telemetry
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(r) for r in reversed(rows)]

    def events(self, limit: int = 100) -> list[dict]:
        with self.connect() as db:
            rows = db.execute(
                """
                SELECT
                    timestamp,
                    'device' type,
                    device,
                    state || ' (' || COALESCE(reason, '') || ')' message
                FROM device_state
                UNION ALL
                SELECT
                    timestamp,
                    'control',
                    COALESCE(device, 'system'),
                    command || ' -> ' || result
                FROM control_action
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]

    def log_action(
        self,
        source: str,
        device: str | None,
        command: str,
        result: str,
    ) -> None:
        with self.connect() as db:
            db.execute(
                """
                INSERT INTO control_action(
                    timestamp,
                    source,
                    device,
                    command,
                    result
                )
                VALUES(?, ?, ?, ?, ?)
                """,
                (self.now(), source, device, command, result),
            )

    def energy_summary(self) -> dict:
        with self.connect() as db:
            rows = db.execute(
                """
                SELECT e.device, e.operating_mode, e.estimated_energy_wh
                FROM energy e
                JOIN (
                    SELECT device, operating_mode, MAX(id) id
                    FROM energy
                    GROUP BY device, operating_mode
                ) x ON e.id = x.id
                """
            ).fetchall()
        by_mode = {"AUTO": {}, "CONVENTIONAL": {}}
        for r in rows:
            by_mode.setdefault(r["operating_mode"], {})[r["device"]] = r[
                "estimated_energy_wh"
            ]
        automated = sum(by_mode.get("AUTO", {}).values())
        conventional = sum(by_mode.get("CONVENTIONAL", {}).values())
        saved = conventional - automated
        ratio = (saved / conventional * 100) if conventional > 0 else 0.0
        return {
            "automatedWh": automated,
            "conventionalWh": conventional,
            "savedWh": saved,
            "savingRatioPct": ratio,
            "byMode": by_mode,
            "model": "estimated: nominal power x runtime",
        }

    def clear(self) -> None:
        with self.connect() as db:
            for table in ("telemetry", "device_state", "energy", "control_action"):
                db.execute(f"DELETE FROM {table}")
