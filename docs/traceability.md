# Requirement Traceability

| Methodology feature | Implementation | Status |
|---|---|---|
| Temperature/humidity | DHT22, `sensor_manager.*`, telemetry/UI | Complete |
| Occupancy | PIR, `occupancy_manager.*` hold timer | Complete |
| Ambient illuminance | LDR, guarded approximate conversion | Simulation approximation |
| AC/fan/light control | `control_policy.*`, relays | Complete |
| Projector control | button, relay, cool-down state machine | Complete |
| Manual override | serial + MQTT + REST + UI | Complete |
| Runtime | `DeviceRecord`, telemetry/API/UI | Complete |
| Energy information | `EnergyTracker`, SQLite/API/UI | Estimated model |
| Wi-Fi/cloud logging | MQTT to local backend/SQLite | Complete; runtime needs broker |
| Dashboard/history | FastAPI, REST/SSE, canvas chart | Complete |
| Control records | `control_action` and event API | Complete |
| Conventional comparison/ratio | mode, energy aggregation, dashboard | Complete |
| Prototype testing | Python policy/API suite + manual matrix | Complete; simulator manual |

