# MQTT Contract

The prototype uses three short topics. Device states are included in telemetry, so a separate state topic would duplicate data without adding research value.

| Topic | Publisher | Subscriber |
|---|---|---|
| `smartclassroom/telemetry` | ESP32 | FastAPI service |
| `smartclassroom/control` | FastAPI service | ESP32 |
| `smartclassroom/mode` | FastAPI service | ESP32 |

## Telemetry

```json
{
  "device_id": "classroom-01",
  "boot_id": "boot-a12-3e8",
  "sequence": 42,
  "uptime_ms": 126000,
  "occupancy": true,
  "temperature_c": 29.4,
  "humidity_pct": 61.0,
  "lux": 130,
  "light": true,
  "fan": true,
  "cooling": false,
  "mode": "SMART",
  "light_runtime_seconds": 600,
  "fan_runtime_seconds": 480,
  "cooling_runtime_seconds": 0,
  "light_switching_events": 1,
  "fan_switching_events": 1,
  "cooling_switching_events": 0,
  "estimated_energy_wh": 30.0,
  "sensor_error": false,
  "mqtt_connected": true
}
```

The firmware value `estimated_energy_wh` is useful for the serial/dashboard demonstration. For persistent analysis, the backend independently computes interval energy from differences in cumulative runtime counters and configured nominal power.

## Mode command

Published to `smartclassroom/mode`:

```json
{"mode": "SMART"}
```

Allowed modes are `SMART`, `CONVENTIONAL`, and `MANUAL`.

## Manual control command

Published to `smartclassroom/control`:

```json
{"device": "fan", "state": true}
```

Allowed devices are `light`, `fan`, and `cooling`. The ESP32 rejects direct state changes unless it is in MANUAL mode. MQTT publish acceptance indicates only delivery to the broker; the next telemetry sample provides the observable applied state.

## Failure behavior

Malformed JSON is rejected without stopping the MQTT loop. If MQTT is unavailable, the API returns `accepted: false`; the dashboard remains usable for stored history and the ESP32 continues local control.
