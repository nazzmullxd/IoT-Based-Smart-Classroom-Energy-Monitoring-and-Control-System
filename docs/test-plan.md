# Test Plan

| Case | Occupancy | Temp °C | Lux | Action | Expected AC | Fan | Light | Projector |
|---|---|---:|---:|---|---|---|---|---|
| Empty/hot/dark | Empty | 32 | 50 | Wait all delays | OFF | OFF | OFF | OFF/cooling |
| Hot/bright | Occupied | 30 | 500 | PIR motion | ON | ON | OFF | OFF |
| Moderate/bright | Occupied | 25.5 | 500 | PIR motion | OFF | ON | OFF | OFF |
| Cool/dark | Occupied | 22 | 80 | PIR motion | OFF | OFF | ON | OFF |
| Hot/dark | Occupied | 30 | 80 | PIR motion | ON | ON | ON | OFF |
| Projector start | Occupied | any | any | Press button | policy | policy | policy | ON |
| Projector stop | any | any | any | Press again | — | — | — | COOLING then OFF |
| Room empties | Empty | any | any | Wait 15 s + delays | delayed OFF | short OFF | timeout OFF | cooling |
| Override | Empty | cool | bright | FORCE_ON AC | ON | OFF | OFF | OFF |
| Network loss | Occupied | 30 | 80 | Stop broker | ON | ON | ON | local control continues |

Automated tests cover thresholds, hysteresis, occupancy hold/renewal, delayed-off cancellation, every override, projector transitions, runtime, energy, ratio guard, backend validation, database writes, and REST routes. Manual Wokwi testing is necessary for interactive sensor widgets and relay wiring.

