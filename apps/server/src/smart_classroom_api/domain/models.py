from typing import Literal

from pydantic import BaseModel, Field


DeviceName = Literal["ac", "fan", "lights", "projector"]
OverrideValue = Literal["AUTO", "FORCE_ON", "FORCE_OFF"]


class ControlRequest(BaseModel):
    value: OverrideValue


class ModeRequest(BaseModel):
    mode: Literal["AUTO", "CONVENTIONAL"]


class ResetRequest(BaseModel):
    target: Literal["ENERGY", "RUNTIME", "ALL"] = "ALL"


class DeviceTelemetry(BaseModel):
    state: Literal["ON", "OFF", "COOLING_DOWN"]
    override: OverrideValue = "AUTO"
    runtimeSeconds: float = Field(default=0, ge=0)
    transitions: int = Field(default=0, ge=0)
    reason: str = "UNKNOWN"
    estimatedEnergyWh: float = Field(default=0, ge=0)


class Telemetry(BaseModel):
    deviceId: str
    uptimeMs: int = Field(ge=0)
    temperatureC: float | None = None
    humidityPct: float | None = None
    illuminanceLux: float = Field(default=0, ge=0)
    ldrRaw: int = 0
    occupied: bool = False
    pirRaw: bool = False
    dark: bool = False
    sensorError: bool = False
    mode: Literal["AUTO", "CONVENTIONAL"] = "AUTO"
    devices: dict[DeviceName, DeviceTelemetry]
    estimatedEnergyWh: dict[str, float] = Field(default_factory=dict)
    network: dict[str, bool] = Field(default_factory=dict)
