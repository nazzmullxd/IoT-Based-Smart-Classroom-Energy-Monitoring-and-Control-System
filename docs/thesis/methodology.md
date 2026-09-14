# Research Methodology

## 1. Proposed Method

### Occupancy sensing

The PIR produces a motion signal. Let the latest motion time be (t_m), current time be (t), and configured hold be \(\tau_o\). Effective occupancy is:

$$
O_e(t)=1 \quad \text{if motion is active or } t-t_m < \tau_o
$$

After the hold expires without new motion, \(O_e(t)=0\). The hold reduces premature switching when occupants are present but temporarily stationary. The simulation uses 15 seconds for a visible demonstration; offline thesis experiments default to 600 seconds.

### Illumination-aware lighting

When effectively occupied, lighting turns on at or below `LIGHT_ON_LUX` and remains on until lux reaches `LIGHT_OFF_LUX`. With defaults of 150 and 250 lux:

$$
L(t)=
\begin{cases}
1, & O_e=1 \land I\le150 \text{ and light was off}\\
0, & O_e=0 \text{ or } I\ge250 \text{ and light was on}\\
L(t-1), & \text{otherwise}
\end{cases}
$$

The gap is hysteresis and prevents repeated switching near one threshold.

### Temperature-aware fan and cooling

The fan uses 28 °C on and 26 °C off thresholds. Cooling uses the higher 29 °C on and 28 °C off thresholds. Each device remains in its prior state inside its hysteresis band. Both require effective occupancy in SMART mode. A missing/invalid temperature does not cause a previously off thermal load to activate.

This is a rule-based operating policy rather than a building thermal model. In Wokwi, cooling activation does not cause the DHT22 temperature to fall automatically.

### Local decisions and communication

Sensor acquisition, occupancy hold, hysteresis, and device transitions run on the ESP32. MQTT carries observations and simple commands but is not inside the automatic decision loop. FastAPI and SQLite provide observation, history, and energy reporting. Therefore automatic operation does not depend on broker/backend availability.

## 2. Baseline Method

CONVENTIONAL is defined as scheduled operation: light, fan, and cooling are on throughout the scenario interval. Temporary vacancy, daylight, and temperature do not cause automatic switching. This is an explicit repeatable baseline chosen for the experiment; it should not be generalized as the behavior of all existing classrooms.

MANUAL is a demonstration/test mode and is not a main comparison group.

## 3. Experimental Protocol

The primary design is a paired deterministic simulation:

1. Select a scenario containing timestamp, actual occupancy, temperature, and lux.
2. Replay the complete sequence using CONVENTIONAL.
3. Reset all controller state and counters.
4. Replay the identical sequence using SMART.
5. Integrate each active device's nominal power over every interval.
6. Compare energy, runtime, switching, delay, and environment-aware metrics.

Thus each comparison uses the **same scenario, same duration, and same environmental inputs; only the control strategy differs**. The CSV file and configuration values should be retained with reported results. A change to thresholds, timeout, nominal powers, or scenario data constitutes a new experimental configuration.

The supplied eight scenarios cover a normal day, high occupancy, intermittent occupancy, long vacancy, high temperature, high daylight, cloudy/low daylight, and rapidly changing occupancy.

## 4. Energy Equations

For device \(i\), nominal power \(P_i\) in watts and active runtime \(t_i\) in hours give:

$$
E_i=P_i\times t_i
$$

Total estimated energy is:

$$
E_{total}=E_{light}+E_{fan}+E_{cooling}
$$

Estimated saving is:

$$
Saving(\%)=
\frac{E_{baseline}-E_{proposed}}
{E_{baseline}}\times100
$$

When baseline energy is zero, the implementation reports zero rather than dividing by zero.

All values produced from Wokwi or offline replay are **estimated energy based on runtime and nominal power**, not actually measured mains energy.

## 5. Evaluation Metrics

### Energy and runtime

- Total and per-device estimated energy in Wh or kWh.
- Estimated absolute saving \(E_b-E_s\) and percentage saving.
- Per-device runtime and total active-device runtime, where simultaneous device runtimes are summed.

### Control activity

- Switching events: count of state transitions across the three devices.
- Activation delay: time from a condition becoming eligible to corresponding activation. With timestamp-level deterministic rules this is zero; a physical experiment should measure sensor-to-output latency.
- Shutdown delay: time from a shutdown trigger to deactivation. Occupancy-driven SMART shutdown equals the selected hold; threshold-driven shutdown is immediate in the reference model.

### Environment-aware performance

Occupied illumination sufficiency is:

$$
100\times\frac{t_{occupied,\ I\ge I_{on}\ or\ light\ on}}{t_{occupied}}
$$

Thermal demand response is the fraction of occupied high-temperature time for which fan or cooling is active. The analysis also reports the fraction of occupied input time inside a selected 20–30 °C band. Because the replay does not simulate thermal feedback, neither metric proves achieved thermal comfort.

### Reliability

Local autonomy is evaluated qualitatively by disconnecting MQTT/backend, varying Wokwi temperature/lux/PIR inputs, and confirming that outputs still follow the ESP32 SMART rules. This test concerns control continuity, not data-delivery reliability.

## 6. Ablation Study

The runner optionally evaluates:

- `CONVENTIONAL`: all devices on.
- `OCCUPANCY_ONLY`: all devices follow effective occupancy.
- `OCCUPANCY_ILLUMINATION`: lighting uses lux; thermal loads follow occupancy.
- `OCCUPANCY_TEMPERATURE`: thermal loads use temperature; lighting follows occupancy.
- `SMART_NO_HYSTERESIS`: all sensors are used with single thresholds.
- `SMART`: the complete proposed controller.

Use `--include-ablation` to generate `ablation_results.csv`. Ablations remain offline so the demonstration dashboard stays understandable.

## 7. Statistical Analysis

The supplied results are deterministic scenario comparisons, so descriptive paired results are appropriate: per-scenario differences, percentages, device runtimes, and switching counts. Means and dispersion may be reported across scenarios only as summaries of these selected cases—not as population estimates.

Inferential tests require independent repeated observations (for example, multiple physical classroom days under randomized/counterbalanced strategies). After collecting such data, state the sampling unit, check distributional assumptions, report confidence intervals and effect sizes, and use a paired test appropriate to the data. The current scripts deliberately do not manufacture statistical significance from deterministic scenarios.

## 8. Reproduction

```powershell
uv run --project apps/server --extra research python experiments/run_experiment.py --include-ablation
uv run --project apps/server --extra research python experiments/analyze_results.py
```

Core outputs are `combined_results.csv`, `energy_by_scenario.csv`, `runtime_comparison.csv`, `saving_summary.csv`, and five PNG figures in `experiments/figures/`.

## 9. Limitations

- PIR senses motion and may label stationary occupants as absent after the hold.
- DHT22 and LDR values are simulated unless physical sensors are connected.
- LDR-derived lux is approximate and not calibrated against a reference meter.
- Nominal power ratings may differ from real appliance draw and ignore power factor/transients.
- Energy values are estimated rather than measured at the mains.
- Cooling is represented as a binary load without a compressor cycle or room thermal model.
- Scenario values are constructed profiles rather than measurements from a full classroom deployment.
- MQTT disconnection tests do not establish long-term hardware reliability.

These limitations constrain claims to **estimated energy reduction under the evaluated operating scenarios**.
