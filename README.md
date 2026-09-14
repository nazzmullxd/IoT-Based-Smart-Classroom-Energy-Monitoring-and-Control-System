# IoT-Based Smart Classroom Energy Monitoring and Control System

A lightweight research prototype for the undergraduate thesis:

> **Design and Experimental Evaluation of an IoT-Based Smart Classroom Energy Management System Using Occupancy, Thermal, and Illumination-Aware Control**

The prototype asks whether a locally autonomous, sensor-aware controller can reduce unnecessary classroom appliance runtime compared with scheduled conventional operation while maintaining appropriate environmental conditions. It is designed for explanation, demonstration, and reproducible comparison—not commercial deployment.

## 1. Project Overview

An ESP32 reads PIR occupancy, DHT22 temperature, and LDR illumination; applies the control policy locally; and controls lighting, fan, and a low-voltage cooling representation. MQTT transports telemetry and simple commands. FastAPI stores observations in SQLite and serves a one-page polling dashboard. Offline scripts replay identical classroom scenarios through CONVENTIONAL and SMART strategies.

## 2. Research Motivation

Scheduled classroom operation can leave lights and thermal loads active during vacancies or when daylight and temperature make them unnecessary. The proposed controller combines occupancy, illumination, and temperature while avoiding rapid relay switching through hysteresis and avoiding premature shutdown through an occupancy hold.

## 3. Research Question

> Can occupancy-, temperature-, and illumination-aware automated control reduce unnecessary classroom energy consumption compared with conventional classroom operation while maintaining appropriate classroom environmental conditions?

## 4. Proposed Architecture

```text
PIR ─────────────┐
DHT22 ──────────►│ ESP32 local control ──► LIGHT / FAN / COOLING
LDR ─────────────┘          │
                            │ MQTT
                            ▼
                       Mosquitto
                            │
                            ▼
                    FastAPI ── SQLite
                            │
                            ▼
                    polling dashboard
```

The ESP32 remains the automatic-control authority. Sensor sampling and appliance decisions continue if Wi-Fi, MQTT, FastAPI, or the dashboard is unavailable. See [architecture.md](docs/architecture/architecture.md).

## 5. Hardware and Simulation Components

| Component | Purpose | ESP32 pin |
|---|---|---:|
| PIR | Motion/occupancy input | GPIO 13 |
| DHT22 | Temperature and supporting humidity telemetry | GPIO 15 |
| LDR module | Approximate ambient lux | GPIO 34 |
| Light indicator/relay | Lighting representation | GPIO 21 |
| Fan indicator/relay | Fan representation | GPIO 22 |
| Cooling indicator/relay | AC/cooling representation | GPIO 23 |

The cooling output should remain a low-voltage LED or small DC fan for this thesis prototype. Actual mains switching is not required. The LDR conversion is isolated in `SensorManager`, making a later BH1750 substitution straightforward.

## 6. Smart Control Algorithm

SMART mode applies:

- Occupancy hold: the room remains effectively occupied for a configurable period after the last PIR motion.
- Lighting: occupied and lux ≤ 150 turns the light on; lux ≥ 250 turns it off.
- Fan: occupied and temperature ≥ 28 °C turns the fan on; temperature ≤ 26 °C turns it off.
- Cooling: occupied and temperature ≥ 29 °C turns cooling on; temperature ≤ 28 °C turns it off.
- Vacancy: after the occupancy timeout, all three loads turn off.

Separated on/off thresholds implement hysteresis. Firmware values are centralized in [config.h](apps/firmware/include/smart_classroom/config.h); experiment values are centralized in [config.py](experiments/config.py).

## 7. Conventional Baseline

CONVENTIONAL represents scheduled classroom usage: light, fan, and cooling remain on for the complete evaluated scenario, regardless of occupancy, temperature, or daylight. It is an explicit experimental baseline, not a claim about every real classroom.

The three firmware modes are:

- `SMART`: full proposed local control.
- `CONVENTIONAL`: scheduled-operation baseline.
- `MANUAL`: direct dashboard/MQTT on/off commands for demonstrations.

## 8. MQTT Architecture

| Topic | Direction | Purpose |
|---|---|---|
| `smartclassroom/telemetry` | ESP32 → backend | Sensors, mode, device states, runtime, estimated energy |
| `smartclassroom/control` | backend → ESP32 | Manual device command |
| `smartclassroom/mode` | backend → ESP32 | SMART/CONVENTIONAL/MANUAL selection |

The backend tolerates malformed messages and broker downtime. Details and payload examples are in [mqtt.md](docs/architecture/mqtt.md).

## 9. Energy Estimation

For each device:

$$E_i=P_i\times t_i$$

with power in watts, runtime in hours, and estimated energy in watt-hours. Total energy is the sum of light, fan, and cooling estimates. The paired comparison is:

$$Saving(\%)=\frac{E_{conventional}-E_{smart}}{E_{conventional}}\times100$$

Default nominal ratings are 120 W lighting, 75 W fan, and 1500 W cooling. These are configurable assumptions.

> **Energy consumption reported by the Wokwi simulation is estimated using nominal device power and recorded runtime and does not constitute direct mains-energy measurement.**

## 10. Experimental Methodology

[scenarios.csv](experiments/scenarios.csv) contains eight simulated classroom profiles: normal day, high occupancy, intermittent occupancy, long vacancy, high temperature, high daylight, cloudy/low daylight, and rapidly changing occupancy. Each timestamped occupancy/temperature/lux sequence is replayed unchanged through both controllers, providing paired inputs.

Optional ablations are `OCCUPANCY_ONLY`, `OCCUPANCY_ILLUMINATION`, `OCCUPANCY_TEMPERATURE`, and `SMART_NO_HYSTERESIS`. The complete protocol is in [methodology.md](docs/thesis/methodology.md).

## 11. Evaluation Metrics

Generated summaries include estimated total/per-device energy, estimated saving percentage, device runtime, total switching events, activation/shutdown delays, occupied-time illumination sufficiency, and thermal-demand response. The thermal metric is an operating-condition proxy because the scenario does not model closed-loop room thermodynamics.

## 12. Running the Simulation

Requirements: Python 3.11–3.13, `uv`, PlatformIO, Mosquitto, VS Code Wokwi extension, and the Wokwi Private IoT Gateway when connecting the simulation to a host-local broker.

1. Install Python dependencies:

   ```powershell
   uv sync --project apps/server --extra dev --extra research
   ```

2. Start Mosquitto:

   ```powershell
   mosquitto -c infra/mosquitto/mosquitto.conf -v
   ```

3. Start FastAPI from the repository root:

   ```powershell
   uv run --project apps/server uvicorn smart_classroom_api.main:app --reload --host 127.0.0.1 --port 8000
   ```

4. Build the firmware:

   ```powershell
   pio run -d apps/firmware
   ```

5. Open `apps/firmware` as the VS Code workspace and run **Wokwi: Start Simulator**. The configured broker is `host.wokwi.internal`; this requires Wokwi's Private IoT Gateway to reach host Mosquitto.

6. Open <http://127.0.0.1:8000>. FastAPI also serves its small OpenAPI view at <http://127.0.0.1:8000/docs>.

Docker is not required. The main workflow is Mosquitto → FastAPI → Wokwi → dashboard.

## 13. Running Experiments

Run the paired study and analysis:

```powershell
uv run --project apps/server --extra research python experiments/run_experiment.py
uv run --project apps/server --extra research python experiments/analyze_results.py
```

Include all ablations with:

```powershell
uv run --project apps/server --extra research python experiments/run_experiment.py --include-ablation
```

Outputs are written to `experiments/results/` and `experiments/figures/`.

## 14. Dashboard

The single page shows sensor values, three appliance states/runtimes, operating mode, manual controls, estimated SMART-versus-CONVENTIONAL energy, a comparison chart, and recent observations. It polls the five-purpose API every two seconds; there is no SSE or frontend build step.

The complete public API is intentionally small:

- `GET /api/status`
- `GET /api/history?limit=100`
- `GET /api/energy`
- `POST /api/mode` with `{"mode":"SMART|CONVENTIONAL|MANUAL"}`
- `POST /api/control` with `{"device":"light|fan|cooling","state":true|false}`

## 15. Example Experiment

The included `normal_classroom_day` scenario runs from 08:00 to 16:00 with three occupied teaching blocks and intervening vacancies. With the default nominal ratings and thresholds:

| Metric | CONVENTIONAL | SMART |
|---|---:|---:|
| Estimated energy | 13,560.0 Wh | 5,927.5 Wh |
| Light runtime | 8.00 h | 1.17 h |
| Fan runtime | 8.00 h | 3.83 h |
| Cooling runtime | 8.00 h | 3.67 h |
| Switching events | 3 | 10 |
| Estimated reduction | — | 56.29% |

This result is generated from a simulated input scenario and nominal power model. It is an **estimated energy reduction under the evaluated operating scenario**, not a measured classroom saving.

## 16. Physical Prototype

The same ESP32 control structure can use a physical PIR, DHT22, LDR or BH1750, LED, and small DC fan. A later metered study should add calibrated, isolated measurement hardware and qualified electrical installation; it should not infer mains consumption from the simulation.

## 17. Current Limitations

- Sensors and loads are simulated unless physical components are connected.
- LDR lux is approximate and uncalibrated.
- Energy is runtime-based estimation, not direct electrical measurement.
- Cooling does not change the scenario temperature; thermal dynamics are simplified.
- PIR detects motion rather than counting occupants and can miss stationary people.
- Results depend on nominal power and scenario assumptions.
- No full classroom deployment or long-term reliability trial has been performed.

## 18. Future Work

Calibrate or replace the light sensor, measure each load with safe certified hardware, model or measure room thermal response, repeat paired trials across real classrooms, quantify sensor/control uncertainty, and apply suitable inferential statistics after collecting independent repeated trials.

## Repository Structure

```text
apps/
├── firmware/       ESP32 local controller and Wokwi circuit
├── server/         compact FastAPI/SQLite/MQTT service and tests
└── dashboard/      one-page HTML/CSS/JavaScript dashboard
experiments/        scenarios, replay controller, analysis, results, figures
docs/
├── architecture/   system and MQTT contracts
└── thesis/         research methodology and thesis mapping
infra/mosquitto/    local broker configuration
data/               ignored local SQLite runtime files
```

## Tests

```powershell
uv run --project apps/server --extra dev pytest -q
uv run --project apps/server python -m compileall apps/server/src experiments
node --check apps/dashboard/app.js
uv run --project apps/server python -m json.tool apps/firmware/diagram.json > $null
pio run -d apps/firmware
```

The focused suite covers threshold behavior, hysteresis, occupancy timeout, SMART and CONVENTIONAL modes, energy equations, malformed MQTT input, API commands, SQLite interval energy, and missing latest telemetry.
