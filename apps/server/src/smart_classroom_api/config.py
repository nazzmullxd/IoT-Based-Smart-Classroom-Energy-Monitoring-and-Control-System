import os
from dataclasses import dataclass
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]


@dataclass(frozen=True)
class Settings:
    database_path: Path
    dashboard_path: Path
    mqtt_host: str = "localhost"
    mqtt_port: int = 1883
    mqtt_enabled: bool = True

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            database_path=Path(
                os.getenv(
                    "DATABASE_PATH",
                    str(REPOSITORY_ROOT / "data" / "smart_classroom.db"),
                )
            ),
            dashboard_path=Path(
                os.getenv(
                    "DASHBOARD_PATH",
                    str(REPOSITORY_ROOT / "apps" / "dashboard"),
                )
            ),
            mqtt_host=os.getenv("MQTT_HOST", "localhost"),
            mqtt_port=int(os.getenv("MQTT_PORT", "1883")),
            mqtt_enabled=os.getenv("MQTT_ENABLED", "true").lower() == "true",
        )
