# Validation Record

Latest validation: 2026-09-15 (Windows, Python 3.13), Phase 1 baseline/stabilization pass.

| Check | Result |
|---|---|
| `uv sync --project apps/server --extra dev` | PASS |
| `uv run --project apps/server --extra dev pytest -q` | PASS; 26 tests |
| `uv run --project apps/server python -m compileall apps/server/src` | PASS |
| `uv run --project apps/server python -m json.tool apps/firmware/diagram.json` | PASS |
| `uvx platformio run -d apps/firmware` | PASS; firmware BIN and ELF generated |
| Firmware memory | RAM 45,148 / 327,680 bytes (13.8%); flash 757,717 / 1,310,720 bytes (57.8%) |
| Live Uvicorn startup | PASS on 127.0.0.1:8000 |
| Live `/`, `/docs`, `/api/status`, and `/static/js/app.js` | PASS; HTTP 200 |
| `docker compose -f infra/compose.yaml config` | NOT TESTED; Docker command unavailable |
| Wokwi CLI lint | NOT TESTED; CLI unavailable |
| Wokwi simulation | NOT TESTED; VS Code extension/private gateway required |
| MQTT end-to-end | NOT TESTED; Mosquitto unavailable |

The server dependencies and tests were run through the isolated `apps/server` uv project. PlatformIO was run through `uvx`. Docker, Wokwi CLI, and Mosquitto are not installed in this environment, so those checks remain external/manual until the tools are available. JSON validity is confirmed, but it is not presented as a substitute for Wokwi CLI lint.
