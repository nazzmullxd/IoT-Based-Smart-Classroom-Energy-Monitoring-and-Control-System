# IoT-Based Smart Classroom Energy Monitoring and Control System

An academic, presentation-ready prototype that reduces unattended classroom energy use. A Wokwi ESP32 reads temperature, humidity, motion, and ambient light; controls four relay outputs locally; publishes telemetry over MQTT; and feeds a FastAPI/SQLite dashboard with history, overrides, runtime, estimated energy, and conventional-versus-automated comparison.

## Architecture

`DHT22 + PIR + LDR → ESP32 policy → relays/loads → Wi-Fi/MQTT → FastAPI/SQLite → REST/SSE dashboard`

The local service emulates a cloud platform so the complete project can be demonstrated without a paid account. See the [architecture](docs/architecture.md), [requirements](docs/requirements.md), [traceability](docs/traceability.md), [product design plan](docs/product-design-plan.md), concrete [implementation blueprint](docs/implementation-blueprint.md), and reusable [start-to-finish implementation prompt](docs/finish-project-prompt.md).

## Repository structure

```text
apps/
├── firmware/     PlatformIO ESP32 firmware, Wokwi circuit, and simulator config
├── server/       FastAPI package and its unit/integration tests
└── dashboard/    dependency-light HTML/CSS/JavaScript dashboard
data/             local runtime database (ignored by Git)
docs/             requirements, architecture, validation, plans, and source material
infra/            Docker Compose and Mosquitto configuration
scenarios/        demonstration scenarios
```

Generated caches, compiled firmware, local databases, virtual environments, and secrets are not source code and are ignored.

## Features

- Local automation continues when Wi-Fi, MQTT, or the backend is unavailable.
- PIR occupancy hold, temperature/lux hysteresis, and non-blocking delayed shutdowns.
- Projector OFF/ON/COOLING_DOWN state machine and physical button.
- AUTO/FORCE_ON/FORCE_OFF per device through serial, MQTT, REST, and dashboard.
- Per-device runtime/transitions and clearly labeled estimated energy.
- AUTO and assumed CONVENTIONAL experimental modes with a division-safe saving ratio.
- Validated telemetry, SQLite history/action logs, REST API, SSE, and responsive dashboard.

## Install and run the server

The recommended Python workflow uses [uv](https://docs.astral.sh/uv/):

```powershell
uv sync --project apps/server --extra dev
uv run --project apps/server uvicorn smart_classroom_api.main:app --reload --host 0.0.0.0 --port 8000
```

Open <http://localhost:8000>. OpenAPI is available at <http://localhost:8000/docs>.

Environment variables are documented in `.env.example`. The default database is `data/smart_classroom.db`, and the default dashboard path is `apps/dashboard`.

## Start MQTT

With a local Mosquitto installation:

```powershell
mosquitto -c infra/mosquitto/mosquitto.conf -v
```

Or start MQTT and the server together:

```powershell
docker compose -f infra/compose.yaml up
```

## Build and simulate firmware

Build from the repository root:

```powershell
pio run -d apps/firmware
```

If `pio` is unavailable, open `apps/firmware` as the workspace folder in VS Code with the PlatformIO IDE extension and build there. Then run **Wokwi: Start Simulator** from that firmware workspace. `apps/firmware/wokwi.toml` points to the generated BIN/ELF.

Wokwi uses `Wokwi-GUEST`. The ESP32 broker hostname is `host.wokwi.internal`, not `localhost`. Reaching a broker on the host computer requires Wokwi's Private IoT Gateway.

The circuit sources are [diagram.json](apps/firmware/diagram.json) and [wokwi.toml](apps/firmware/wokwi.toml). A license-independent [SVG circuit diagram](docs/circuit-diagram.svg) is also available.

## Pin map

| Component | ESP32 pin |
|---|---:|
| DHT22 DATA | GPIO 15 |
| PIR OUT | GPIO 13 |
| LDR AO | GPIO 34 (input-only) |
| AC / Fan / Light / Projector relay | GPIO 23 / 22 / 21 / 19 |
| Projector button | GPIO 27, internal pull-up |

## Demonstration

1. Start the broker, server, and simulation; wait for telemetry.
2. Trigger PIR motion. Occupancy remains active for 15 seconds after motion ends.
3. Set DHT22 temperature above 28 °C. AC and fan activate; lower it to observe hysteresis and delayed shutdown.
4. Lower illuminance below 150 lux while occupied. Lights activate; raise it above 220 lux to observe delayed shutdown.
5. Press the projector button while occupied. Press again to observe its 8-second COOLING_DOWN state.
6. Let occupancy expire and watch the automatic shutdown sequence.
7. Use AUTO, ON, and OFF on each dashboard equipment card.
8. Compare AUTO and CONVENTIONAL estimated energy using the [experiment procedure](docs/energy-experiment.md).

## REST API

- `GET /api/status`, `/api/telemetry/latest`, `/api/telemetry/history?limit=100`
- `GET /api/devices`, `/api/energy`, `/api/events`
- `POST /api/control/{ac|fan|lights|projector}` with `{"value":"AUTO|FORCE_ON|FORCE_OFF"}`
- `POST /api/mode` with `{"mode":"AUTO|CONVENTIONAL"}`
- `POST /api/reset` with `{"target":"ENERGY|RUNTIME|ALL"}`

## Serial commands

At 115200 baud: `STATUS`, `MODE AUTO`, `MODE CONVENTIONAL`, `AC|FAN|LIGHT|PROJECTOR AUTO|ON|OFF`, `RESET ENERGY`, and `RESET RUNTIME`.

## Energy model

Wokwi values are **estimated energy**, calculated as `nominal watts × runtime hours`, not measured consumption. Defaults are 1500 W AC, 75 W fan, 120 W lights, and 300 W projector. The saving ratio is `(conventional − automated) / conventional × 100`; a zero conventional value returns zero.

The CONVENTIONAL policy is an explicit experiment assumption: AC, fan, and lights stay on while the projector remains manual.

## Tests

```powershell
uv run --project apps/server --extra dev pytest
uv run --project apps/server python -m compileall apps/server/src
uv run --project apps/server python -m json.tool apps/firmware/diagram.json > $null
```

If installed, run `wokwi-cli lint apps/firmware/diagram.json`. The manual hardware matrix is in [test-plan.md](docs/test-plan.md).

## Troubleshooting

- **`pio` missing:** install/enable PlatformIO IDE, then build the `apps/firmware` project.
- **Wrong Wokwi firmware path:** confirm `apps/firmware/.pio/build/esp32dev/firmware.bin` and `.elf` match `apps/firmware/wokwi.toml`.
- **No dashboard data:** inspect ESP32 serial output, Mosquitto logs, and `GET /api/status`.
- **Backend port conflict:** choose another Uvicorn port and open that URL.
- **MQTT unavailable:** run with `$env:MQTT_ENABLED="false"` when only the API/dashboard is being tested.
- **Database issue:** confirm the process can write to `data/` or the configured `DATABASE_PATH`.

## Limitations

Lux is approximate and uncalibrated. Relays/LEDs do not simulate mains power, current, inrush, power factor, thermal dynamics, or true projector control. A physical deployment requires calibrated sensors, certified metering, electrical isolation and correctly rated contactors, device-specific projector/AC commands, authenticated TLS MQTT, realistic timers, and qualified electrical installation.

The preserved source methodology is [docs/source/proposed-methodology.md](docs/source/proposed-methodology.md).
