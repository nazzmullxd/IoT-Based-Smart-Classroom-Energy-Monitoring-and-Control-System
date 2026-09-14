# Thesis Mapping

| Thesis section | Software/evidence |
|---|---|
| Introduction and motivation | README research question and baseline rationale |
| Literature/conceptual background | Occupancy control, hysteresis, delayed shutdown, MQTT, runtime-energy model |
| Proposed system architecture | `docs/architecture/architecture.md`, Wokwi `diagram.json` |
| Hardware and sensor design | `apps/firmware/src/sensors/`, firmware pin/config file |
| Control algorithm | firmware `control_policy.cpp`, `occupancy_manager.cpp`, reference `experiments/controller.py` |
| IoT communication | firmware `network_manager.cpp`, backend `mqtt_client.py`, MQTT contract |
| Data logging and dashboard | backend `database.py`/`main.py`, single-page dashboard |
| Experimental design | `docs/thesis/methodology.md`, `experiments/scenarios.csv`, replay runner |
| Results | generated CSV summaries and publication-style PNG figures |
| Discussion | per-scenario trade-offs: energy, runtime, switching, condition proxies |
| Limitations and future work | methodology and README limitations sections |

The firmware demonstrates the proposed physical/control architecture. The offline experiment runner provides reproducible comparative evidence. The two share the same named thresholds and state logic, but results should identify whether they came from Wokwi/live telemetry or offline scenario replay.
