from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


Mode = Literal["SMART", "CONVENTIONAL", "MANUAL"]
Device = Literal["light", "fan", "cooling"]


class Telemetry(BaseModel):
    model_config = ConfigDict(extra="ignore")

    timestamp: datetime | None = None
    device_id: str = "classroom-01"
    boot_id: str | None = None
    sequence: int | None = Field(default=None, ge=0)
    uptime_ms: int = Field(default=0, ge=0)
    occupancy: bool
    temperature_c: float | None = None
    humidity_pct: float | None = None
    lux: float = Field(ge=0)
    light: bool
    fan: bool
    cooling: bool
    mode: Mode
    light_runtime_seconds: float = Field(default=0, ge=0)
    fan_runtime_seconds: float = Field(default=0, ge=0)
    cooling_runtime_seconds: float = Field(default=0, ge=0)
    light_switching_events: int = Field(default=0, ge=0)
    fan_switching_events: int = Field(default=0, ge=0)
    cooling_switching_events: int = Field(default=0, ge=0)
    estimated_energy_wh: float = Field(default=0, ge=0)
    sensor_error: bool = False
    mqtt_connected: bool = False


class ModeRequest(BaseModel):
    mode: Mode


class ControlRequest(BaseModel):
    device: Device
    state: bool
