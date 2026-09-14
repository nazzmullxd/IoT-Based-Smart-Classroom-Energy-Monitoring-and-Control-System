
# MASTER IMPLEMENTATION guide — IoT Smart Classroom Energy Monitoring and Control System

You are the lead embedded-systems, IoT, simulation, backend, dashboard, testing, and documentation engineer for this project.

Your job is to inspect the existing project workspace, read the methodology document, derive the requirements from it, and then IMPLEMENT a complete, working, well-documented prototype of the system.

Do not merely explain how to build it.

Do not stop after producing a plan.

Create and modify the actual project files, build the firmware, validate what you can locally, fix errors you encounter, and leave the repository in a usable state.

---

# 1. PRIMARY SOURCE OF TRUTH

The repository should contain this file:

`Proposed_Methodology_Anonymous.md`

Before writing any implementation code:

1. Locate this Markdown file.
2. Read the ENTIRE file from beginning to end.
3. Treat it as the primary source of functional requirements.
4. Do not overwrite or rewrite this source file.
5. Extract the system requirements from it.
6. Identify which requirements are:

   * explicitly required by the methodology,
   * implementation choices needed to make the prototype runnable,
   * simulation approximations caused by Wokwi limitations.

If the exact filename is not found, search the workspace for Markdown files containing the title:

`IoT-Based Smart Classroom Energy Monitoring and Control System`

Do not begin implementation until you understand the source document.

Create:

`docs/requirements.md`

Summarize the extracted requirements there.

Clearly divide the document into:

* Source-derived requirements
* Implementation decisions
* Simulation assumptions
* Wokwi limitations
* Future physical-hardware improvements

Never present an implementation assumption as something stated in the methodology.

---

# 2. PROJECT OBJECTIVE

Build a complete simulated prototype for an:

**IoT-Based Smart Classroom Energy Monitoring and Control System**

The solution should demonstrate this end-to-end architecture:

Sensors
↓
ESP32 edge controller
↓
Device-control / relay layer
↓
Wi-Fi / MQTT communication
↓
Telemetry/data-storage service
↓
REST API
↓
Digital dashboard

The prototype must demonstrate:

* classroom environmental sensing,
* classroom occupancy sensing,
* ambient-light sensing,
* ESP32-based decision making,
* AC control,
* fan control,
* classroom-light control,
* projector control,
* occupancy-based energy management,
* delayed and controlled shutdown behavior,
* manual override,
* device runtime measurement,
* energy-consumption estimation or measurement,
* telemetry,
* historical logging,
* dashboard visualization,
* control-action logging,
* automated vs conventional energy comparison,
* calculation of Energy Saving Ratio.

---

# 3. DEVELOPMENT ENVIRONMENT

Use this stack unless the existing workspace contains a better compatible setup.

## Embedded firmware

* ESP32
* Arduino framework
* PlatformIO
* C++

## Simulation

* Wokwi
* Wokwi for VS Code
* `diagram.json`
* `wokwi.toml`

Prefer:

`board-esp32-devkit-c-v4`

unless compatibility testing gives a reason to use another standard ESP32 board.

## Backend

Prefer a lightweight local Python backend because the project should be easy for a student to run.

Recommended:

* Python 3
* FastAPI
* built-in SQLite via `sqlite3`
* Paho MQTT client
* Uvicorn

## MQTT

Prefer a local Mosquitto broker.

Provide a Docker Compose configuration if practical, but do not make Docker the only possible way of running the project.

The ESP32 running inside Wokwi should connect to local host services using the currently documented Wokwi networking mechanism such as:

`host.wokwi.internal`

Verify current Wokwi documentation before hard-coding assumptions if Internet/documentation access is available.

## Dashboard

Use a lightweight browser dashboard served by the backend.

Prefer:

* HTML
* CSS
* vanilla JavaScript

Avoid unnecessary frontend frameworks unless there is a strong technical reason.

The dashboard should work locally and be easy to demonstrate during a university/project presentation.

---

# 4. FIRST PHASE — INSPECT THE EXISTING WORKSPACE

Before creating files:

1. List the repository structure.
2. Read `Proposed_Methodology_Anonymous.md`.
3. Look for:

   * existing PlatformIO configuration,
   * existing ESP32 firmware,
   * existing `diagram.json`,
   * existing `wokwi.toml`,
   * existing backend,
   * existing dashboard,
   * existing README,
   * existing tests.
4. Preserve useful existing work.
5. Do not blindly replace functional code.
6. Detect the user's OS when possible from the environment.
7. Check whether these commands/tools are available:

   * `pio`
   * `platformio`
   * `python`
   * `pip`
   * `docker`
   * `docker compose`
   * `mosquitto`
   * `wokwi-cli`

Report missing external dependencies in documentation, but continue implementing everything that does not depend on them.

---

# 5. CREATE A DEVELOPMENT PLAN

After reading the methodology, write:

`docs/implementation-plan.md`

Include:

1. methodology requirement,
2. corresponding implementation,
3. Wokwi component,
4. ESP32 software module,
5. backend/dashboard feature,
6. verification method.

Use a traceability table.

Example columns:

| Requirement | Source | Implementation | Verification |
| ----------- | ------ | -------------- | ------------ |

Then proceed with implementation immediately.

Do not stop and wait for approval.

---

# 6. HARDWARE SIMULATION REQUIREMENTS

Create a Wokwi circuit representing the classroom system.

Use supported Wokwi components where possible.

The simulated hardware should include at minimum:

* 1 × ESP32
* 1 × DHT22
* 1 × PIR motion sensor
* 1 × photoresistor/LDR module
* 4 × relay modules
* 4 × visual loads/LED indicators representing:

  * AC
  * Fan
  * Classroom Lights
  * Projector
* appropriate resistors for LEDs if necessary
* 1 × projector/manual-control pushbutton
* optional additional buttons for demonstration/manual override if useful
* clear Wokwi text labels if supported

Use actual relay components rather than controlling only LEDs directly, because the methodology specifies device-control modules/relays.

LEDs may be placed on the relay outputs to visually represent the real electrical appliances.

Label them clearly:

* AC
* FAN
* LIGHT
* PROJECTOR

---

# 7. INITIAL PIN ASSIGNMENT

Use a clear, conflict-free ESP32 pin map.

A reasonable initial configuration is:

* DHT22 DATA → GPIO 15
* PIR OUT → GPIO 13
* LDR AO → GPIO 34
* LDR DO → optional GPIO 35 if useful
* AC relay → GPIO 23
* Fan relay → GPIO 22
* Light relay → GPIO 21
* Projector relay → GPIO 19
* Projector/manual button → GPIO 27

Validate that all selected pins are appropriate for their intended ESP32 functions.

GPIO 34/35 are input-only, so use them only as inputs.

If you change any pins, update every relevant file consistently:

* firmware configuration,
* `diagram.json`,
* documentation,
* tests.

Create a central configuration header instead of scattering pin numbers throughout the program.

For example:

`include/config.h`

---

# 8. WOKWI DIAGRAM

Create:

`diagram.json`

It must contain the complete circuit.

Requirements:

* valid Wokwi JSON,
* meaningful part IDs,
* neat approximate physical arrangement,
* sensible wiring,
* no floating required inputs,
* shared ground where appropriate,
* visible appliance indicators,
* clear component placement,
* valid pin names,
* valid supported Wokwi part types.

Use current Wokwi documentation to verify component IDs and pin names if available.

Do not invent unsupported Wokwi components.

Run:

`wokwi-cli lint`

if Wokwi CLI is installed.

Fix all lint errors.

If the CLI is unavailable, manually validate the JSON as thoroughly as possible.

---

# 9. PLATFORMIO CONFIGURATION

Create or update:

`platformio.ini`

Use an ESP32 Arduino environment.

Configure required libraries, preferably with explicit dependency declarations.

Expected dependencies may include:

* an ESP32-compatible DHT22 library,
* PubSubClient for MQTT,
* ArduinoJson if JSON serialization is used.

Avoid unnecessary libraries.

Ensure:

`pio run`

successfully produces ESP32 firmware.

Do not consider the firmware phase complete until compilation succeeds, unless the required compiler/toolchain is not installed.

If build tools are unavailable, document the exact missing dependency and still ensure the source is structurally correct.

---

# 10. WOKWI CONFIGURATION

Create:

`wokwi.toml`

Point it to the actual PlatformIO-generated ESP32:

* firmware `.bin`
* ELF file

Use paths appropriate for the actual PlatformIO environment name.

If useful, configure:

* serial forwarding,
* network forwarding,
* GDB server support,

but do not add unnecessary complexity.

The project should be runnable from VS Code using:

`Wokwi: Start Simulator`

after building the PlatformIO project.

---

# 11. FIRMWARE ARCHITECTURE

Do not write one giant `main.cpp`.

Use modular design.

A suitable structure is:

`src/main.cpp`

`include/config.h`

`include/models.h`

`include/control_policy.h`

`src/control_policy.cpp`

`include/sensor_manager.h`

`src/sensor_manager.cpp`

`include/device_manager.h`

`src/device_manager.cpp`

`include/occupancy_manager.h`

`src/occupancy_manager.cpp`

`include/energy_tracker.h`

`src/energy_tracker.cpp`

`include/network_manager.h`

`src/network_manager.cpp`

`include/telemetry_manager.h`

`src/telemetry_manager.cpp`

Adapt this if a simpler structure is clearly better.

Keep hardware-independent decision logic separated from hardware I/O wherever possible so it can be tested.

---

# 12. SENSOR DATA MODEL

Define a model for sensor readings containing at least:

* timestamp / uptime
* temperature °C
* relative humidity %
* occupancy state
* PIR raw state
* ambient illumination in lux when practical
* raw LDR/ADC reading
* dark/bright state

Handle invalid DHT readings.

Do not let a temporary invalid DHT read crash or destabilize the controller.

Use the previous valid value when appropriate and record sensor-error state.

---

# 13. DHT22

Use the DHT22 for:

* temperature,
* humidity.

The dashboard should show both.

The methodology refers to environmental conditions, but does not specify exact humidity-based switching thresholds.

Therefore:

* include humidity in telemetry and policy inputs,
* do not invent a strong humidity control rule and claim it came from the methodology,
* if you add an optional humidity-assisted rule, make it configurable and disabled by default or clearly document it as an implementation assumption.

---

# 14. AMBIENT LIGHT

Use the Wokwi photoresistor module.

Prefer its analog output so the system can report an approximate illumination value rather than only bright/dark.

Convert the simulated analog reading to lux using an appropriate transfer function compatible with the Wokwi component.

Protect against:

* division by zero,
* infinite lux,
* invalid ADC values.

Also derive a configurable darkness condition such as:

`lux < LIGHT_ON_LUX_THRESHOLD`

Use hysteresis if useful to prevent relay chatter.

Do not claim the simulated lux conversion is a calibrated physical measurement.

Document that real hardware requires sensor calibration.

---

# 15. OCCUPANCY LOGIC

The PIR sensor should detect motion.

Do NOT make occupancy disappear immediately when PIR output becomes LOW.

Implement an occupancy hold timer.

Conceptually:

* PIR motion detected → occupied = true
* remember last motion timestamp
* remain occupied for configurable timeout
* after timeout without new motion → unoccupied

For demonstration, use a shorter simulation timeout.

Create separate configurable values if useful:

* simulation timeout,
* recommended real-world timeout.

Do not hard-code timing values throughout the firmware.

---

# 16. DEVICE CONTROL MODEL

Represent each device with an explicit state.

At minimum:

* OFF
* ON

For the projector, use a richer state machine:

* OFF
* ON
* COOLING_DOWN

For devices with delayed shutdown, track pending shutdown timing properly.

Do not use blocking `delay()` calls for long operational logic.

Use `millis()` based non-blocking timing.

The main loop must remain responsive to:

* sensors,
* buttons,
* networking,
* telemetry,
* dashboard commands.

---

# 17. AC CONTROL

Implement the methodology's intent:

AC control considers:

* occupancy,
* environmental conditions.

Recommended prototype behavior:

If occupied and temperature is above configurable AC-on threshold:
→ AC ON.

Use hysteresis.

Example concept:

* AC ON at ≥ 28°C
* AC OFF below ≤ 26°C

Treat these numbers as implementation defaults, not methodology facts.

Make them easy to change in `config.h`.

For unoccupied shutdown:

* implement a delayed OFF timer,
* cancel the pending shutdown if occupancy returns before timer expiration.

Log all state changes with reasons.

Example reason codes:

* `TEMP_HIGH`
* `TEMP_NORMAL`
* `UNOCCUPIED_TIMEOUT`
* `MANUAL_OVERRIDE`

---

# 18. FAN CONTROL

Fan control should consider:

* occupancy,
* temperature/environment.

Recommended initial behavior:

* occupied + temperature ≥ configurable fan threshold → ON
* otherwise OFF after a short configurable delay.

Use hysteresis if helpful.

Fan shutdown may be immediate or short-delay as described by the methodology.

Make the chosen behavior configurable and document it.

---

# 19. CLASSROOM LIGHT CONTROL

Lights should depend on:

* classroom occupied,
* ambient illumination low.

Conceptually:

`occupied && lux < configured threshold`

→ lights ON.

When unoccupied:

* start an unoccupied timeout,
* turn lights OFF after the timeout,
* cancel timeout if occupancy returns.

Use a suitable lux threshold as a simulation default and clearly mark it as an implementation assumption.

---

# 20. PROJECTOR CONTROL

The methodology specifies manual/controlled operation and a controlled cool-down cycle.

Implement this carefully.

Projector should:

* require manual activation,
* preferably only allow activation while classroom is occupied,
* remain controllable through dashboard/manual override,
* enter COOLING_DOWN state instead of abruptly losing power.

State machine:

OFF
→ manual request
→ ON

ON
→ shutdown request / occupancy policy
→ COOLING_DOWN

COOLING_DOWN
→ configured cooldown elapsed
→ OFF

During COOLING_DOWN:

* keep the simulated power relay active if that best models real projector cooling,
* clearly expose `COOLING_DOWN` on telemetry/dashboard,
* ignore or safely handle conflicting requests.

For Wokwi demonstration use a short cooldown such as several seconds.

Document that physical projector shutdown timing depends on the real projector manufacturer's requirements.

---

# 21. MANUAL OVERRIDE

The methodology explicitly requires manual override functionality.

Support three logical control modes per device where practical:

* AUTO
* FORCE_ON
* FORCE_OFF

Dashboard controls should allow the user to change override mode.

Safety/policy constraints:

* define exactly how manual override interacts with occupancy rules,
* avoid ambiguous behavior,
* display override status prominently,
* log every override action.

For projector, preserve cool-down safety even when a force-off request occurs.

---

# 22. OPERATING MODES FOR EVALUATION

Implement at least two experiment modes:

### AUTO

Uses the complete smart energy-management logic.

### CONVENTIONAL / BASELINE

Represents a configurable conventional classroom-control scenario used only for comparison.

The methodology requires comparison between conventional and automated control but does not define the exact conventional behavior.

Therefore clearly document the baseline as an experimental assumption.

A reasonable baseline simulation is:

* after a classroom session begins, selected devices are manually left ON,
* environmental/occupancy automation does not automatically save energy,
* projector remains separately manual if appropriate,
* session ends only through explicit reset/end-session action.

If you choose another defensible baseline, document the reasoning.

Never claim the baseline definition came directly from the source document.

---

# 23. DEVICE RUNTIME TRACKING

Track runtime independently for:

* AC
* Fan
* Lights
* Projector

Maintain at minimum:

* current state,
* current ON interval start,
* cumulative runtime,
* transition count.

Expose runtime:

* through Serial,
* through MQTT telemetry,
* through REST API,
* on dashboard.

Use milliseconds internally and convert appropriately for human display.

---

# 24. ENERGY MONITORING

First investigate whether Wokwi currently provides a practical supported current/power-monitoring component suitable for this project.

If a suitable sensor is supported and reliable:

* use it where reasonable,
* document the implementation.

If Wokwi does NOT provide a suitable power-monitoring component:

implement a clearly labeled:

**Estimated Energy Model**

Use:

`Energy (Wh) = Power (W) × Runtime (hours)`

Provide configurable nominal power values for each simulated appliance, such as:

* AC nominal power
* fan nominal power
* lights nominal power
* projector nominal power

Put them in configuration.

Do not describe estimated energy as physically measured energy.

Dashboard labels should say:

`Estimated Energy`

when that is what is being calculated.

Document how a physical prototype could later use an actual power meter/current sensor.

---

# 25. ENERGY SAVING RATIO

Implement the methodology's equation:

Energy Saving Ratio (%) =

`(E_conventional - E_automated) / E_conventional × 100`

Handle:

`E_conventional = 0`

without division-by-zero.

Expose:

* conventional energy,
* automated energy,
* energy saved,
* energy-saving percentage.

Provide these values in:

* backend,
* REST API,
* dashboard.

Clearly separate simulated/estimated energy from real measured energy.

---

# 26. SERIAL MONITOR OUTPUT

Create readable, structured serial output.

Do not spam the serial console on every loop iteration.

Use a reasonable interval, e.g. once per second or when states change.

Show something similar to:

SMART CLASSROOM STATUS

Temperature: 29.4 C
Humidity: 61.2 %
Illuminance: 75 lux
Occupancy: OCCUPIED

AC: ON
Fan: ON
Lights: ON
Projector: OFF

Mode: AUTO

AC Runtime: ...
Fan Runtime: ...
Light Runtime: ...
Projector Runtime: ...

Estimated Energy: ...
WiFi: CONNECTED
MQTT: CONNECTED

Also print explicit event messages when device states change.

---

# 27. SERIAL COMMAND INTERFACE

Add a small command parser for debugging/demo use if practical.

Useful commands:

`STATUS`

`MODE AUTO`

`MODE CONVENTIONAL`

`AC AUTO`

`AC ON`

`AC OFF`

`FAN AUTO`

`FAN ON`

`FAN OFF`

`LIGHT AUTO`

`LIGHT ON`

`LIGHT OFF`

`PROJECTOR AUTO`

`PROJECTOR ON`

`PROJECTOR OFF`

`RESET ENERGY`

`RESET RUNTIME`

`HELP`

Commands should not block the main loop.

Use this interface both for debugging and automated simulation tests where useful.

---

# 28. WI-FI

Configure ESP32 Wi-Fi for Wokwi.

Default simulation network may use:

SSID:

`Wokwi-GUEST`

No password.

Centralize Wi-Fi settings.

Do not scatter credentials through the code.

Create a secrets/config template if needed.

Do not commit real credentials.

Implement:

* connection state,
* reconnect logic,
* retry interval,
* graceful local control when network is unavailable.

IMPORTANT:

The classroom automation must continue working if Wi-Fi or MQTT fails.

Cloud connectivity must not be required for basic device safety/control.

---

# 29. MQTT ARCHITECTURE

Implement MQTT communication.

Use sensible topic names, for example:

`smartclassroom/telemetry`

`smartclassroom/state`

`smartclassroom/events`

`smartclassroom/commands`

`smartclassroom/availability`

or a structured equivalent.

Telemetry should include JSON.

Example conceptual schema:

{
"deviceId": "classroom-01",
"uptimeMs": 123456,
"temperatureC": 28.4,
"humidityPct": 62.1,
"illuminanceLux": 85,
"occupied": true,
"mode": "AUTO",
"devices": {
"ac": {
"state": "ON",
"override": "AUTO",
"runtimeSeconds": 340
},
"fan": {},
"lights": {},
"projector": {
"state": "COOLING_DOWN"
}
},
"estimatedEnergyWh": {},
"network": {}
}

Use ArduinoJson or a similarly safe approach.

Avoid oversized payloads for ESP32.

---

# 30. MQTT COMMANDS

Allow the backend/dashboard to issue commands.

Commands should support at least:

* device override,
* set AUTO mode,
* operating mode,
* reset energy statistics,
* optionally change thresholds.

Validate every command.

Reject malformed JSON.

Do not allow unknown device names to alter arbitrary memory/state.

Send acknowledgement/event messages after commands.

---

# 31. BACKEND SERVICE

Create:

`backend/`

Build a lightweight local service.

Recommended structure:

`backend/app.py`

`backend/requirements.txt`

`backend/database.py`

`backend/mqtt_service.py`

`backend/models.py`

`backend/static/`

or another clean structure.

Responsibilities:

1. subscribe to ESP32 telemetry,
2. validate incoming messages,
3. persist telemetry,
4. persist device state transitions,
5. persist control actions,
6. expose REST API,
7. serve dashboard,
8. publish remote-control commands,
9. calculate/query historical statistics.

Use SQLite for ease of demonstration.

Do not require a cloud account to demonstrate the project.

Explain in documentation that this local backend represents the methodology's cloud telemetry/storage layer in the simulation prototype.

---

# 32. DATABASE

Use SQLite.

Create tables for at least:

### telemetry

* id
* timestamp
* temperature
* humidity
* illuminance
* occupancy
* operating mode

### device_state

* id
* timestamp
* device
* state
* override mode
* reason

### energy

* id
* timestamp
* device
* runtime
* estimated energy
* operating mode

### control_action

* id
* timestamp
* source
* device
* command
* result

Use reasonable indexes.

Do not store unnecessary duplicate high-frequency information.

Provide database initialization automatically.

The user should not need to manually create tables.

---

# 33. REST API

Expose documented REST endpoints such as:

`GET /api/status`

`GET /api/telemetry/latest`

`GET /api/telemetry/history`

`GET /api/devices`

`GET /api/energy`

`GET /api/events`

`POST /api/control/{device}`

`POST /api/mode`

`POST /api/reset`

Adjust route naming if a cleaner API emerges.

Validate input.

Return useful HTTP errors.

Document the API.

---

# 34. DASHBOARD

Create a professional but simple digital dashboard.

It must show:

## Current environment

* temperature,
* humidity,
* ambient light/lux,
* occupancy.

## Device status

Individual cards/status rows for:

* AC,
* Fan,
* Lights,
* Projector.

For each show:

* ON/OFF/COOLING,
* AUTO/FORCE_ON/FORCE_OFF,
* runtime,
* estimated energy.

## Controls

Allow:

* AUTO,
* ON,
* OFF

as appropriate.

Allow:

* AUTO vs CONVENTIONAL operating mode.

For projector clearly display COOLING_DOWN.

## Energy

Show:

* total automated estimated energy,
* total conventional estimated energy,
* energy saved,
* Energy Saving Ratio (%),
* device-by-device consumption.

## Historical data

Include simple charts for:

* temperature history,
* humidity history,
* ambient-light history,
* occupancy history,
* energy consumption over time.

Use a lightweight chart library only if necessary.

If using an external CDN, document that Internet access is required.

Prefer locally installable or dependency-light solutions.

## Logs

Show recent:

* control actions,
* device state changes,
* sensor/network errors.

Make the UI readable on a laptop during a project presentation.

---

# 35. REAL-TIME DASHBOARD UPDATES

Prefer an efficient real-time update mechanism.

Options include:

* Server-Sent Events,
* WebSocket,
* short polling.

Prefer SSE or another simple mechanism unless there is a reason not to.

The dashboard should visibly update as Wokwi sensor values change.

---

# 36. MQTT BROKER SETUP

Provide a straightforward local Mosquitto configuration.

If Docker is appropriate, create:

`docker-compose.yml`

and:

`mosquitto/mosquitto.conf`

But also document how to run with a manually installed Mosquitto broker.

Do not require paid cloud services.

Expected topology:

Wokwi ESP32
→ MQTT
→ local Mosquitto
→ Python backend
→ SQLite
→ REST/dashboard

For a Wokwi ESP32 accessing a service running on the development computer, use the current recommended Wokwi host connection mechanism.

Do not assume plain `localhost` inside the ESP32 simulation refers to the development computer.

---

# 37. CONFIGURATION

Centralize configurable parameters.

Embedded configuration should include:

* pin assignments,
* DHT interval,
* telemetry interval,
* occupancy timeout,
* AC on threshold,
* AC off threshold,
* fan on threshold,
* fan off threshold,
* lights-on lux threshold,
* lights-off lux threshold,
* AC unoccupied delay,
* fan unoccupied delay,
* lights unoccupied delay,
* projector cooldown duration,
* nominal power ratings,
* MQTT host,
* MQTT port,
* MQTT topics,
* device ID.

Use meaningful names.

Document every non-obvious parameter.

---

# 38. SIMULATION VS REAL HARDWARE

Support a concept such as:

`SIMULATION_MODE`

when useful.

Simulation mode can use:

* short occupancy timeout,
* short shutdown delay,
* short projector cooldown,
* faster telemetry,
* simulated energy values.

Real-world suggested values can be documented separately.

The demonstration should not require waiting several minutes to observe shutdown logic.

---

# 39. AUTOMATED TESTING — CONTROL POLICY

Separate decision logic enough to test it without physical hardware.

Create tests covering at least:

1. empty classroom → unnecessary loads OFF,
2. occupied + high temperature → AC ON,
3. occupied + moderate temperature → fan behavior,
4. occupied + dark → lights ON,
5. occupied + bright → lights OFF,
6. AC hysteresis,
7. fan hysteresis,
8. occupancy timeout,
9. occupancy return cancels pending shutdown,
10. manual FORCE_ON,
11. manual FORCE_OFF,
12. restoring AUTO,
13. projector ON request,
14. projector shutdown enters COOLING_DOWN,
15. projector cooldown reaches OFF,
16. runtime accumulation,
17. estimated-energy calculation,
18. zero conventional energy division guard,
19. energy-saving ratio,
20. Wi-Fi/MQTT failure does not stop local automation.

Use PlatformIO/native tests if feasible.

If not, create another appropriate automated test harness.

---

# 40. WOKWI AUTOMATION SCENARIOS

If Wokwi CLI is installed and current Wokwi Automation Scenario support is usable, create:

`scenarios/`

Example scenarios:

`01_empty_room.yaml`

`02_hot_occupied_room.yaml`

`03_dark_occupied_room.yaml`

`04_occupancy_timeout.yaml`

`05_projector_cooldown.yaml`

`06_manual_override.yaml`

`07_energy_saving_demo.yaml`

Use automation controls where Wokwi currently supports them.

For example:

* adjust DHT22 temperature/humidity if supported,
* adjust photoresistor lux,
* trigger PIR/motion if automation support exists,
* press pushbuttons,
* verify serial messages,
* verify expected output pins where possible.

IMPORTANT:

Wokwi Automation Scenarios may have version-dependent/experimental capabilities.

Verify the current syntax instead of inventing unsupported commands.

If PIR cannot currently be automated through scenarios, document that and make that specific test manual or provide another valid simulation trigger.

---

# 41. MANUAL DEMONSTRATION TEST MATRIX

Create:

`docs/test-plan.md`

Include a table similar to:

| Test | Occupancy | Temp | Lux | Action | Expected AC | Fan | Light | Projector |
| ---- | --------- | ---: | --: | ------ | ----------- | --- | ----- | --------- |

Cover at minimum:

### Case 1

Empty room, hot, dark
Expected: unnecessary devices eventually OFF.

### Case 2

Occupied, hot, bright
Expected: AC/fan according to thresholds, lights OFF.

### Case 3

Occupied, moderate temperature, bright
Expected: fan depending on threshold, AC OFF.

### Case 4

Occupied, cool, dark
Expected: lights ON.

### Case 5

Occupied, hot, dark
Expected: AC + fan + lights ON.

### Case 6

Occupied + projector command
Expected: projector ON.

### Case 7

Projector shutdown
Expected: COOLING_DOWN then OFF.

### Case 8

Classroom becomes empty
Expected: devices shut down according to their configured policies.

### Case 9

Manual override
Expected: override takes precedence according to documented rules.

### Case 10

Network disconnected
Expected: local automatic control still works.

---

# 42. ENERGY-SAVING EXPERIMENT

Create a repeatable demonstration procedure.

Document how to run the same classroom scenario in:

1. CONVENTIONAL mode,
2. AUTO mode.

Record:

* total runtime per device,
* total estimated energy,
* conventional energy,
* automated energy,
* savings,
* Energy Saving Ratio.

Create:

`docs/energy-experiment.md`

Clearly state that Wokwi-derived energy values are simulated/estimated unless a true simulated power sensor is implemented.

Never present these as measurements from a physical classroom.

---

# 43. LOGGING

Create structured event messages for:

* sensor errors,
* occupancy changes,
* device state changes,
* pending shutdown,
* cancelled shutdown,
* projector cooldown,
* Wi-Fi connection,
* MQTT connection,
* MQTT reconnect,
* dashboard commands,
* override changes.

Each important device transition should include its reason.

Example:

`[EVENT] AC ON reason=TEMP_HIGH temperature=29.2 occupancy=1`

This will make project demonstrations and debugging much easier.

---

# 44. ERROR HANDLING

Handle at minimum:

* invalid DHT readings,
* invalid LDR conversion,
* MQTT broker unavailable,
* Wi-Fi unavailable,
* malformed MQTT command,
* backend unavailable,
* database initialization errors,
* divide-by-zero in energy calculations,
* `millis()` timing behavior,
* button debounce,
* MQTT reconnect without blocking the controller.

Do not use infinite blocking loops waiting for network connections.

---

# 45. CODE QUALITY REQUIREMENTS

Firmware must be:

* non-blocking where practical,
* modular,
* readable,
* appropriately commented,
* free from giant functions,
* free from unnecessary global state,
* consistent in naming,
* configurable.

Backend must be:

* modular,
* documented,
* input validated,
* easy to run.

Dashboard must be:

* understandable,
* not overdesigned,
* useful for demonstration.

Avoid premature complexity.

Do not add features unrelated to the methodology until core requirements are complete.

---

# 46. README

Create a comprehensive:

`README.md`

Include:

## Project title

## Problem statement

## System architecture

## Methodology mapping

## Features

## Hardware/Wokwi components

## Pin mapping

## Project directory structure

## Required software

* VS Code
* PlatformIO
* Wokwi extension
* Python
* MQTT broker
* optional Docker
* optional Wokwi CLI

## Installation instructions

## PlatformIO build instructions

## Starting MQTT broker

## Starting backend

## Starting Wokwi

## Opening dashboard

## Testing sensors in Wokwi

Explain exactly how to:

* change DHT22 temperature/humidity,
* trigger PIR occupancy,
* modify ambient light,
* press projector button,
* observe relay states.

## Manual override instructions

## Automated vs conventional experiment

## Energy Saving Ratio

## Troubleshooting

Include common problems:

* PlatformIO missing,
* wrong firmware path,
* Wokwi simulator cannot start,
* MQTT connection failure,
* `host.wokwi.internal` networking problem,
* backend port conflict,
* DHT library error,
* Wokwi CLI/token unavailable.

## Simulation limitations

## Physical prototype migration

---

# 47. ARCHITECTURE DOCUMENTATION

Create:

`docs/architecture.md`

Include a Mermaid diagram showing:

DHT22
PIR
LDR
↓
ESP32
↓
Control Policy
↓
Relay Layer
↓
AC / Fan / Light / Projector

and:

ESP32
↓ MQTT
Mosquitto
↓
Backend
↓
SQLite
↓ REST/SSE
Dashboard

Explain the four methodology layers:

1. Physical Sensing and Actuation
2. Edge Controller
3. Cloud Telemetry and Storage
4. Application Dashboard

For this simulation, explain that the local Python/SQLite service emulates the cloud layer.

---

# 48. REQUIREMENT TRACEABILITY

Create:

`docs/traceability.md`

Map every methodology feature to implementation files.

Example:

| Methodology Requirement | Implementation          | Status                   |
| ----------------------- | ----------------------- | ------------------------ |
| Temperature monitoring  | DHT22 + SensorManager   | Complete                 |
| Humidity monitoring     | DHT22 + SensorManager   | Complete                 |
| Occupancy               | PIR + OccupancyManager  | Complete                 |
| AC control              | ControlPolicy + relay   | Complete                 |
| Fan control             | ControlPolicy + relay   | Complete                 |
| Light control           | LDR + ControlPolicy     | Complete                 |
| Projector control       | Projector state machine | Complete                 |
| Cloud logging           | MQTT/backend            | Complete                 |
| Dashboard               | backend/static          | Complete                 |
| Runtime                 | EnergyTracker           | Complete                 |
| Energy information      | estimated energy model  | Simulation approximation |
| Historical data         | SQLite/API/dashboard    | Complete                 |
| Manual override         | MQTT/API/UI             | Complete                 |
| Energy-saving ratio     | analysis module         | Complete                 |

Do not mark something Complete unless it actually exists.

---

# 49. EXPECTED PROJECT STRUCTURE

Aim for approximately:

smart-classroom/
├── Proposed_Methodology_Anonymous.md
├── README.md
├── platformio.ini
├── wokwi.toml
├── diagram.json
├── docker-compose.yml
├── .gitignore
│
├── include/
│   ├── config.h
│   ├── models.h
│   ├── sensor_manager.h
│   ├── occupancy_manager.h
│   ├── control_policy.h
│   ├── device_manager.h
│   ├── energy_tracker.h
│   ├── network_manager.h
│   └── telemetry_manager.h
│
├── src/
│   ├── main.cpp
│   ├── sensor_manager.cpp
│   ├── occupancy_manager.cpp
│   ├── control_policy.cpp
│   ├── device_manager.cpp
│   ├── energy_tracker.cpp
│   ├── network_manager.cpp
│   └── telemetry_manager.cpp
│
├── backend/
│   ├── app.py
│   ├── database.py
│   ├── mqtt_service.py
│   ├── models.py
│   ├── requirements.txt
│   └── static/
│       ├── index.html
│       ├── app.js
│       └── styles.css
│
├── mosquitto/
│   └── mosquitto.conf
│
├── scenarios/
│   └── ...
│
├── test/
│   └── ...
│
└── docs/
├── requirements.md
├── implementation-plan.md
├── architecture.md
├── test-plan.md
├── energy-experiment.md
└── traceability.md

Change this structure when technically justified.

---

# 50. BUILD AND VALIDATION LOOP

After implementation, perform this loop.

## Firmware

Run:

`pio run`

If it fails:

1. inspect errors,
2. fix them,
3. run again.

Repeat until successful or blocked by an unavailable external dependency.

## JSON

Validate:

`diagram.json`

as valid JSON.

If Wokwi CLI exists:

`wokwi-cli lint`

Fix errors.

## Python

Create/use a virtual environment if appropriate.

Install backend requirements.

Run syntax checks.

Start the backend and make sure it loads.

Check important REST endpoints.

## Tests

Run all unit tests.

Fix failing tests.

## Wokwi

If Wokwi CLI and required token/configuration are available:

* run the simulation,
* inspect serial output,
* execute available automation scenarios,
* fix firmware/simulation issues.

If Wokwi can only be launched through the VS Code extension, make everything ready and document the exact final manual step.

Do not falsely say Wokwi was tested if you could not actually run it.

---

# 51. DO NOT FAKE SUCCESS

This is critical.

When reporting final status, distinguish:

* CREATED
* BUILT
* TESTED
* NOT TESTED
* BLOCKED BY EXTERNAL DEPENDENCY

Examples:

Good:

`Firmware: built successfully with PlatformIO.`

Good:

`Wokwi diagram created and JSON validated, but simulator execution was not possible because Wokwi CLI authentication was unavailable.`

Bad:

`Everything works perfectly.`

unless it was actually tested.

---

# 52. DO NOT ASK UNNECESSARY QUESTIONS

Make reasonable implementation choices yourself.

When the methodology leaves something unspecified:

1. choose a reasonable prototype default,
2. put it in configuration,
3. document it as an assumption,
4. continue.

Examples include:

* threshold temperatures,
* lux threshold,
* timeout duration,
* projector cooldown time,
* appliance wattage,
* MQTT topic naming.

Do not repeatedly stop to ask me to choose these values.

The goal is a working academic prototype.

---

# 53. PRIORITY ORDER

If time, tool, or dependency constraints prevent completing everything at once, prioritize in this exact order:

1. Read methodology
2. Requirements extraction
3. PlatformIO project
4. Valid Wokwi `diagram.json`
5. ESP32 sensor reading
6. Occupancy management
7. Four-device relay control
8. Projector cooldown logic
9. Manual override
10. Runtime tracking
11. Energy estimation
12. Serial logging
13. Unit tests
14. Wokwi testing
15. Wi-Fi
16. MQTT
17. Backend
18. SQLite
19. REST API
20. Dashboard
21. Historical graphs
22. Automated/conventional comparison
23. Wokwi automation scenarios
24. Documentation polish

Never sacrifice reliable core control logic for cosmetic dashboard features.

---

# 54. ACADEMIC INTEGRITY / METHODOLOGY CONSISTENCY

The implementation must remain consistent with the methodology.

Whenever you add something not explicitly specified by the methodology, label it appropriately as:

* implementation choice,
* configurable prototype threshold,
* simulation assumption,
* future hardware recommendation.

Do not silently expand the research claims.

Examples:

If energy is calculated from runtime × nominal power:

call it:

`estimated energy consumption`

not:

`measured energy consumption`.

If the conventional baseline behavior is invented for the experiment:

explicitly state:

`The source methodology requires conventional-vs-automated comparison but does not define a conventional control policy; this implementation uses the following baseline assumption...`

---

# 55. SECURITY / SECRETS

Do not commit:

* MQTT passwords,
* API tokens,
* Wokwi tokens,
* private keys,
* real Wi-Fi credentials.

Provide:

`.env.example`

or appropriate configuration templates.

Add sensitive files to `.gitignore`.

---

# 56. PRESENTATION-FRIENDLY BEHAVIOR

This project will likely be demonstrated.

Make the simulation easy to demonstrate in under a few minutes.

Use short simulation timers.

For example, reasonable simulation-only values might be approximately:

* occupancy timeout: 10–20 seconds,
* AC shutdown delay: several seconds,
* light shutdown delay: several seconds,
* fan shutdown delay: a few seconds,
* projector cooldown: 5–10 seconds.

These are NOT real deployment values.

Put them in configuration.

The presenter should be able to:

1. start the system,
2. trigger occupancy,
3. increase temperature,
4. see fan/AC activate,
5. darken the LDR,
6. see lights activate,
7. activate projector,
8. remove occupancy,
9. watch staged shutdown,
10. observe projector cooldown,
11. see dashboard/history/energy update.

---

# 57. ADD DEMO MODE IF USEFUL

If useful, provide a compile-time or runtime demo mode.

Example:

`DEMO_MODE = true`

Demo mode may use accelerated timers.

Normal mode should have more realistic configurable values.

Document this clearly.

---

# 58. FINAL VERIFICATION CHECKLIST

Before finishing, confirm each item:

* [ ] Methodology Markdown read fully
* [ ] Source file preserved
* [ ] Requirements extracted
* [ ] ESP32 PlatformIO project created
* [ ] PlatformIO compilation successful if tool available
* [ ] DHT22 implemented
* [ ] PIR implemented
* [ ] LDR implemented
* [ ] Lux/dark condition implemented
* [ ] Occupancy timeout implemented
* [ ] AC relay implemented
* [ ] Fan relay implemented
* [ ] Light relay implemented
* [ ] Projector relay implemented
* [ ] AC delayed shutdown implemented
* [ ] Fan shutdown behavior implemented
* [ ] Light unoccupied timeout implemented
* [ ] Projector cooldown state machine implemented
* [ ] Manual override implemented
* [ ] Runtime tracking implemented
* [ ] Energy estimation/measurement implemented
* [ ] Conventional comparison implemented
* [ ] Energy Saving Ratio implemented
* [ ] Serial diagnostics implemented
* [ ] Wi-Fi implemented
* [ ] MQTT implemented
* [ ] MQTT reconnect implemented
* [ ] Local automation works without cloud
* [ ] Backend implemented
* [ ] SQLite implemented
* [ ] REST API implemented
* [ ] Dashboard implemented
* [ ] Historical visualization implemented
* [ ] Control logs implemented
* [ ] Wokwi `diagram.json` implemented
* [ ] `wokwi.toml` implemented
* [ ] Wokwi diagram linted if CLI available
* [ ] Automated tests created
* [ ] Tests executed where possible
* [ ] Wokwi scenarios created where supported
* [ ] README completed
* [ ] Architecture documentation completed
* [ ] Test plan completed
* [ ] Energy experiment documented
* [ ] Requirement traceability completed
* [ ] Simulation limitations documented
* [ ] No fake test-success claims
* [ ] No secrets committed

---

# 59. FINAL RESPONSE FORMAT

When all work possible in the environment is complete, give me a concise engineering report.

Use these sections:

## Completed

List what was actually implemented.

## Architecture

Briefly describe the resulting architecture.

## Files Created/Changed

List important files.

## Build Results

Show whether PlatformIO build succeeded.

## Test Results

Show:

* unit-test result,
* Wokwi lint result,
* Wokwi simulation result,
* backend/API result.

## Assumptions

List implementation assumptions not explicitly specified by the methodology.

## Simulation Limitations

Explain anything Wokwi cannot faithfully reproduce.

## How to Run

Give exact commands, in order.

## Demonstration Procedure

Give exact steps for demonstrating:

1. occupancy,
2. AC,
3. fan,
4. lights,
5. projector,
6. automatic shutdown,
7. manual override,
8. dashboard,
9. energy savings.

## Remaining Manual Steps

Only list steps that genuinely require me, such as:

* installing VS Code extensions,
* authenticating Wokwi,
* supplying a Wokwi CLI token,
* manually starting the VS Code Wokwi simulation if no CLI access exists.

---

# 60. START NOW

Begin by locating and reading:

`Proposed_Methodology_Anonymous.md`

Then inspect the repository.

Create the requirements/traceability plan.

After that, IMPLEMENT the project.

Do not stop after planning.

Work through compilation and validation errors yourself.

Use the methodology as the source of truth and make reasonable, clearly documented prototype assumptions wherever the methodology intentionally leaves implementation details unspecified.
