# Implementation Plan and Traceability

| Methodology requirement | Wokwi component | ESP32 implementation | Backend/dashboard | Verification |
|---|---|---|---|---|
| Temperature/humidity | DHT22 | `SensorManager` with last-valid retention | Live metrics/history | Change DHT controls; inspect API |
| Occupancy | PIR | `OccupancyManager` 15 s hold | Status/history | Policy unit tests/manual timeout |
| Ambient conditions | Photoresistor | guarded lux estimate + hysteresis | Lux metric/chart | Dark/bright tests |
| Four-device control | Four relays + LEDs | `ControlPolicy`/`DeviceManager` | Four control cards | Policy tests/visual relays |
| Projector safety | Relay, LED, button | OFF/ON/COOLING_DOWN | State and override control | Cool-down tests |
| Runtime/energy | Simulated loads | per-device interval accounting | SQLite/API/energy cards | Calculation tests |
| Cloud telemetry/logs | Wi-Fi/MQTT | reconnecting `NetworkManager` | MQTT consumer + SQLite | API integration test |
| Dashboard/control | Browser | validated MQTT commands | REST/SSE/vanilla UI | TestClient/manual browser |
| Energy comparison | Operating mode | AUTO/CONVENTIONAL | comparison API/UI | ratio tests/experiment |

Implementation order: firmware core; circuit; network telemetry; persistence/API; dashboard; tests; documentation; validation.

