# Validation Record

Validation environment: Windows, Python 3.13, 15 September 2026.

| Check | Result |
|---|---|
| Focused pytest suite | PASS: 12 tests |
| Python compileall | PASS |
| Dashboard JavaScript syntax | PASS |
| Wokwi diagram JSON parse | PASS |
| PlatformIO ESP32 build | PASS |
| Firmware RAM | 45,092 / 327,680 bytes (13.8%) |
| Firmware flash | 754,989 / 1,310,720 bytes (57.6%) |
| Scenario replay | PASS: 8 scenarios × 6 strategies, 624 intervals |
| Analysis summaries | PASS |
| Five thesis figures | PASS |
| Live API and dashboard HTML | PASS: page served, five API paths present, no projector/SSE client |
| Interactive responsive browser layout | Manual; in-app browser unavailable in this session |
| Wokwi interactive simulation | Manual; extension/private gateway required |
| Mosquitto end-to-end transport | Manual; local broker required |

The generated results are deterministic simulation outputs using nominal ratings and must not be described as measured mains energy.

## Diagram revision — 19 November 2026

| Check | Result |
|---|---|
| Root and firmware diagram consistency | PASS: identical 40-part diagrams; GPIO and connection references checked |
| Custom appliance WASM build | PASS: Zig 0.17.1; compiled binary included |
| Appliance visual behavior | PASS: actual WASM exercised through a minimal API host; OFF/ON transitions, animation, and return to stationary OFF |
| Visual framebuffers | PASS: generated and inspected light, fan, and cooling ON graphics; ON/OFF PNGs in `docs/assets/appliances` |
| Both simulator configurations | PASS: same chip binary and firmware build paths; firmware artifacts present |
| PlatformIO ESP32 build | PASS: Espressif32 8.0.0 / Arduino-ESP32 3.3.12 |
| Firmware RAM / flash | 47,344 / 327,680 bytes RAM; 914,036 / 1,310,720 bytes flash |
| Full Wokwi layout and electrical behavior | NOT VERIFIED: browser preview attempt blocked by automatic approval review; no detailed reason supplied |
| MQTT end-to-end matrix | Not rerun for this diagram revision |

The current framework introduced its own global `NetworkManager` class. The
project class was renamed to `ClassroomNetwork` to resolve the build collision;
its behavior and the control policy were not changed. The visual checks do not
execute ESP32 firmware or model relay contacts, so the manual matrix in
`test-plan.md` still needs to be run in Wokwi.

## Local Wokwi run — 19 November 2026

Started the installed VS Code Wokwi simulator through its normal UI. The
initial run exposed a custom-chip allocation of 259 WASM pages, exceeding
Wokwi's 64-page limit. A 64 KiB stack reduces the corrected three-appliance
module to 9 pages. The live run also exposed shared graphics state; each of
the three chip instances now receives separate storage. Automated checks
cover both the memory limit and three-instance display isolation.

Observed the firmware running in SMART mode at 29 C / 100 lux: initially
unoccupied with all outputs OFF, PIR motion turning all outputs ON, and
the occupancy timeout turning them OFF again in serial output. After the
graphics correction, the live simulator loaded all three displays and showed
the illuminated light, active fan, and cooling airflow together. The
simulation was left running. MQTT reported OFFLINE, so this run does not
validate the backend/dashboard or the full manual test matrix.
