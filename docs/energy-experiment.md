# Repeatable Energy Experiment

The values in this experiment are simulations based on nominal watts × firmware runtime; they are not physical classroom measurements.

1. Start broker, backend, firmware, and dashboard; send `RESET ENERGY`.
2. Select `CONVENTIONAL`. Run a fixed 60-second session: occupied 0–30 s, unoccupied 30–60 s; hot (30 °C) and dark (80 lux) throughout. Record device runtimes and total conventional Wh.
3. Reset, select `AUTO`, and repeat exactly the same sensor timeline. Record automated Wh.
4. The API/dashboard computes `saved = conventional - automated` and `ratio = saved / conventional × 100`. When conventional energy is zero, ratio is reported as zero.
5. Export results by saving `GET /api/energy`, `GET /api/telemetry/history`, and `GET /api/events` responses.

The baseline is an implementation assumption because the methodology asks for comparison but does not define conventional behavior. Here AC/fan/lights remain on throughout the conventional session; projector stays manual.

