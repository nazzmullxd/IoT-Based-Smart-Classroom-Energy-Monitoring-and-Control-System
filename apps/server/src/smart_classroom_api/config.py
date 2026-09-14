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
    light_power_w: float = 120.0
    fan_power_w: float = 75.0
    cooling_power_w: float = 1500.0
    light_on_lux: float = 150.0
    light_off_lux: float = 250.0
    fan_on_temp_c: float = 28.0
    fan_off_temp_c: float = 26.0
    cooling_on_temp_c: float = 29.0
    cooling_off_temp_c: float = 28.0
    occupancy_timeout_seconds: float = 600.0

    def __post_init__(self) -> None:
        if not self.light_on_lux < self.light_off_lux:
            raise ValueError("LIGHT_ON_LUX must be lower than LIGHT_OFF_LUX")
        if not self.fan_off_temp_c < self.fan_on_temp_c:
            raise ValueError("FAN_OFF_TEMP_C must be lower than FAN_ON_TEMP_C")
        if not self.cooling_off_temp_c < self.cooling_on_temp_c:
            raise ValueError(
                "COOLING_OFF_TEMP_C must be lower than COOLING_ON_TEMP_C"
            )
        if not self.fan_on_temp_c < self.cooling_on_temp_c:
            raise ValueError("Cooling must activate above the fan threshold")
        if self.occupancy_timeout_seconds < 0:
            raise ValueError("OCCUPANCY_TIMEOUT_SECONDS cannot be negative")

    @classmethod
    def from_env(cls) -> "Settings":
        root = REPOSITORY_ROOT
        return cls(
            database_path=Path(
                os.getenv("DATABASE_PATH", str(root / "data" / "smart_classroom.db"))
            ),
            dashboard_path=Path(
                os.getenv("DASHBOARD_PATH", str(root / "apps" / "dashboard"))
            ),
            mqtt_host=os.getenv("MQTT_HOST", "localhost"),
            mqtt_port=int(os.getenv("MQTT_PORT", "1883")),
            mqtt_enabled=os.getenv("MQTT_ENABLED", "true").lower() == "true",
            light_power_w=float(os.getenv("LIGHT_POWER_W", "120")),
            fan_power_w=float(os.getenv("FAN_POWER_W", "75")),
            cooling_power_w=float(os.getenv("COOLING_POWER_W", "1500")),
            light_on_lux=float(os.getenv("LIGHT_ON_LUX", "150")),
            light_off_lux=float(os.getenv("LIGHT_OFF_LUX", "250")),
            fan_on_temp_c=float(os.getenv("FAN_ON_TEMP_C", "28")),
            fan_off_temp_c=float(os.getenv("FAN_OFF_TEMP_C", "26")),
            cooling_on_temp_c=float(os.getenv("COOLING_ON_TEMP_C", "29")),
            cooling_off_temp_c=float(os.getenv("COOLING_OFF_TEMP_C", "28")),
            occupancy_timeout_seconds=float(
                os.getenv("OCCUPANCY_TIMEOUT_SECONDS", "600")
            ),
        )

    @property
    def powers(self) -> dict[str, float]:
        return {
            "light": self.light_power_w,
            "fan": self.fan_power_w,
            "cooling": self.cooling_power_w,
        }
