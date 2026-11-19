# Annotated classroom simulator

Open the repository root in VS Code, build with `pio run -d apps/firmware`,
then run **Wokwi: Start Simulator**. Opening `apps/firmware` as the workspace
also works. Both configurations load the same ESP32 firmware and bundled
`chips/appliance.chip.wasm` visual component. A Wokwi extension/license is
needed for interactive simulation; the chip binary is already included.

`apps/firmware/diagram.json` is the authoritative diagram. The root
`diagram.json` is an identical copy for the root-workspace entry point.
After future edits, copy the authoritative file to the root and run the
diagram check below.

## Reading the diagram

Read the four numbered columns from left to right: sensors, ESP32, relays,
and appliances. Local labels identify each sensor's purpose and GPIO, and
each appliance's GPIO, nominal rating, and ON/OFF thresholds. The footer
contains the shared SMART rules, power legend, energy estimate, and IoT path.
Detailed explanations and demonstration cases are kept in this guide.
The IoT arrows describe software communication, not electrical connections;
topic names and payloads are in [mqtt.md](architecture/mqtt.md).

| Signal | ESP32 pin | Meaning |
|---|---:|---|
| DHT22 SDA | 15 | Temperature for fan/cooling; humidity for telemetry |
| PIR OUT | 13 | Motion; effective occupancy includes a hold |
| LDR AO | 34 | ADC input converted to approximate lux |
| Light relay IN | 21 | Lighting command |
| Fan relay IN | 22 | Fan command |
| Cooling relay IN | 23 | Cooling command |

Red wires carry 3.3 V, purple wires carry 5 V, and black wires are ground.
Cyan wires carry sensor signals. Orange, green, and blue identify lighting,
fan, and cooling control/switched signals respectively. Relays retain the
existing `transistor: pnp` configuration; firmware commands are active HIGH.
Confirm actual COM-to-NO polarity in the interactive simulator before a demo.

The fixture illuminates, the fan rotates, and the cooling unit shows moving
airflow when their relay's NO contact supplies a HIGH to the visual's SW pin.
SW has an internal pull-down so an open contact returns to OFF. The graphics
are simulator instrumentation, not physical appliances or an added display
connected to the ESP32. They do not draw modeled appliance current and they
do not change sensor readings. The former projector/button assembly was
removed because the application only implements light, fan, and cooling.

## Demonstration

Start in SMART mode. Click PIR and select **Simulate Motion** before each
occupied case; repeat motion if needed to keep the 15-second hold active.
Click DHT22 and LDR to adjust their values. Allow a sensor sampling interval
(2 seconds) before judging the outputs.

| Inputs while occupied | Expected visuals |
|---|---|
| 24 C, 100 lux | Light ON; fan/cooling OFF |
| 28 C, 500 lux, starting with cooling OFF | Fan ON; light/cooling OFF |
| 30 C, 500 lux | Fan/cooling ON; light OFF |
| 140 -> 200 -> 260 lux | Light ON -> stays ON -> OFF |
| Stop motion | All OFF 15 seconds after the final PIR HIGH |

PIR's simulated HIGH pulse lasts 2 seconds. The occupancy hold starts from
the last HIGH, not from the moment the motion button was clicked. The
physical-mode firmware setting and offline experiments use 600 seconds.
Hysteresis means a device holds its previous state between its ON/OFF
thresholds. Fan and cooling can run simultaneously.

Use the existing dashboard/MQTT controls to select CONVENTIONAL (all three
ON) or MANUAL (explicit device states). These bypass SMART occupancy rules.
The serial monitor reports state every 5 seconds; MQTT telemetry is sent
every 3 seconds when connected. Host-local MQTT requires the Private IoT
Gateway and Mosquitto described in the README.

Energy remains nominal watts multiplied by runtime hours: light 120 W,
fan 75 W, cooling 1500 W. The visual's 3.3 V input does not represent those
power ratings. Cooling does not lower the DHT22 temperature automatically.

## Rebuilding and checking

The supplied WASM file lets users run without a separate chip compilation
step. After changing the C drawing/animation implementation:

```powershell
uv run --with ziglang==0.17.1 python tools/build_appliance.py
pio run -d apps/firmware
uv run --with wasmtime==44.0.0 python tools/check_diagram.py
```

The check verifies identical diagrams, connection references, GPIO mappings,
configured build paths, and the compiled visual's OFF/ON transitions. A
minimal Wokwi API host exercises the actual WASM, checks that animation
stops at OFF, and writes its real framebuffers into `docs/assets/appliances`.
This test does not simulate ESP32 execution or relay electrical behavior.

The Wokwi API header is vendored from
[wokwi/inverter-chip](https://github.com/wokwi/inverter-chip), with its MIT
license in `apps/firmware/chips/LICENSE.wokwi-api`.
See [Wokwi custom displays](https://docs.wokwi.com/chips-api/chip-json) and
[custom-chip configuration](https://docs.wokwi.com/vscode/project-config#custom-chips)
for the supported extension mechanism.

## Interactive acceptance checks

Open both workspace entry points and confirm all three custom displays load.
Inspect labels and wire routes at normal zoom. On boot, relay contacts and
visuals must be OFF; motion at the initial 29 C / 100 lux should activate
all three. Check each transition against serial output, including shutdown
after vacancy. Complete the manual matrix in [test-plan.md](test-plan.md).
These checks require the actual Wokwi simulator and are distinct from the
automated visual-component checks above.
