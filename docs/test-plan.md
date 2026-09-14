# Focused Test Plan

## Automated

Run `uv run --project apps/server --extra dev pytest -q`.

The suite verifies lighting and temperature thresholds, hysteresis, occupancy timeout, SMART vacancy behavior, CONVENTIONAL scheduled behavior, energy equations and zero-baseline guard, SQLite interval energy, missing telemetry responses, simple mode/manual API commands, and malformed MQTT handling.

## Manual Wokwi matrix

| Case | Occupancy | Temperature | Lux | Expected SMART output |
|---|---|---:|---:|---|
| Empty, hot, dark | Unoccupied after hold | 32 °C | 50 | All off |
| Occupied, cool, dark | Occupied | 24 °C | 100 | Light on; fan/cooling off |
| Occupied, warm, bright | Occupied | 28 °C | 500 | Fan on; light/cooling off |
| Occupied, hot, bright | Occupied | 30 °C | 500 | Fan and cooling on; light off |
| Light hysteresis | Occupied | 24 °C | 140→200→260 | On→on→off |
| Thermal hysteresis | Occupied | 29→28.5→26 °C | 500 | Thermal loads on→on→off |
| Occupancy hold | Motion then none | 30 °C | 100 | Loads remain on until timeout, then off |
| Broker loss | Occupied | change values | change values | Local outputs still follow policy |
| Conventional | any | any | any | All three loads on |
| Manual | any | any | any | Only dashboard-selected states |

Wokwi and MQTT end-to-end checks remain manual because they require the simulator extension/private gateway and local broker.
