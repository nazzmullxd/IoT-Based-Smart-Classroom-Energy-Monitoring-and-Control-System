import argparse
import csv
from datetime import datetime
from pathlib import Path

from controller import DEVICES, ExperimentalController
import config


ROOT = Path(__file__).resolve().parent
DEFAULT_SCENARIOS = ROOT / "scenarios.csv"
RESULTS = ROOT / "results"


def seconds(value: str) -> float:
    parsed = datetime.strptime(value, "%H:%M:%S" if value.count(":") == 2 else "%H:%M")
    return parsed.hour * 3600 + parsed.minute * 60 + parsed.second


def load_scenarios(path: Path) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            grouped.setdefault(row["scenario"], []).append(
                {
                    "timestamp": row["timestamp"],
                    "time_seconds": seconds(row["timestamp"]),
                    "occupancy": row["occupancy"].strip().lower() in {"1", "true", "occupied"},
                    "temperature_c": float(row["temperature_c"]),
                    "lux": float(row["lux"]),
                }
            )
    for rows in grouped.values():
        rows.sort(key=lambda item: item["time_seconds"])
    return grouped


def result_row(
    scenario: str,
    strategy: str,
    sample: dict,
    end_seconds: float,
    controller: ExperimentalController,
    changes: dict[str, bool],
) -> dict:
    duration = end_seconds - sample["time_seconds"]
    runtimes, energies = controller.integrate(duration)
    occupied_seconds = duration if sample["occupancy"] else 0.0
    sufficient = occupied_seconds if (sample["lux"] >= config.LIGHT_ON_LUX or controller.state["light"]) else 0.0
    thermal_comfort = occupied_seconds if config.THERMAL_RANGE_MIN_C <= sample["temperature_c"] <= config.THERMAL_RANGE_MAX_C else 0.0
    thermal_demand = occupied_seconds if sample["temperature_c"] >= config.FAN_ON_TEMP_C else 0.0
    thermal_response = thermal_demand if (controller.state["fan"] or controller.state["cooling"]) else 0.0
    return {
        "scenario": scenario,
        "mode": strategy,
        "timestamp": sample["timestamp"],
        "duration_seconds": duration,
        "occupancy": sample["occupancy"],
        "effective_occupancy": controller.effective_occupancy,
        "temperature_c": sample["temperature_c"],
        "lux": sample["lux"],
        **{device: controller.state[device] for device in DEVICES},
        **{f"{device}_runtime_seconds": runtimes[device] for device in DEVICES},
        **{f"{device}_energy_wh": energies[device] for device in DEVICES},
        "estimated_energy_wh": sum(energies.values()),
        "switching_events": len(changes),
        "activation_events": sum(changes.values()),
        "activation_delay_seconds": 0.0,
        "shutdown_events": sum(not state for state in changes.values()),
        "shutdown_delay_seconds": sum(
            config.OCCUPANCY_TIMEOUT_SECONDS
            for state in changes.values()
            if not state and not controller.effective_occupancy
        ),
        "occupied_seconds": occupied_seconds,
        "sufficient_illumination_seconds": sufficient,
        "thermal_comfort_seconds": thermal_comfort,
        "thermal_demand_seconds": thermal_demand,
        "thermal_response_seconds": thermal_response,
    }


def replay(scenario: str, samples: list[dict], strategy: str) -> list[dict]:
    controller = ExperimentalController(strategy)
    results: list[dict] = []
    for index, sample in enumerate(samples[:-1]):
        end = samples[index + 1]["time_seconds"]
        changes = controller.evaluate(
            sample["occupancy"], sample["temperature_c"], sample["lux"], sample["time_seconds"]
        )
        expiry = controller.occupancy_expiry()
        if expiry is not None and sample["time_seconds"] < expiry < end:
            results.append(result_row(scenario, strategy, sample, expiry, controller, changes))
            split = dict(sample)
            split["timestamp"] = f"{int(expiry // 3600):02d}:{int(expiry % 3600 // 60):02d}:{int(expiry % 60):02d}"
            split["time_seconds"] = expiry
            changes = controller.evaluate(False, split["temperature_c"], split["lux"], expiry)
            results.append(result_row(scenario, strategy, split, end, controller, changes))
        else:
            results.append(result_row(scenario, strategy, sample, end, controller, changes))
    return results


def write_rows(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay identical classroom inputs through control strategies.")
    parser.add_argument("--scenarios", type=Path, default=DEFAULT_SCENARIOS)
    parser.add_argument("--include-ablation", action="store_true")
    args = parser.parse_args()
    modes = config.ABLATION_MODES if args.include_ablation else ("CONVENTIONAL", "SMART")
    scenarios = load_scenarios(args.scenarios)
    by_mode: dict[str, list[dict]] = {mode: [] for mode in modes}
    for scenario, samples in scenarios.items():
        for mode in modes:
            by_mode[mode].extend(replay(scenario, samples, mode))

    RESULTS.mkdir(parents=True, exist_ok=True)
    write_rows(RESULTS / "conventional_results.csv", by_mode["CONVENTIONAL"])
    write_rows(RESULTS / "smart_results.csv", by_mode["SMART"])
    combined = [row for mode in modes for row in by_mode[mode]]
    write_rows(RESULTS / "combined_results.csv", combined)
    if args.include_ablation:
        write_rows(RESULTS / "ablation_results.csv", combined)
    print(f"Replayed {len(scenarios)} scenarios in {len(modes)} modes; wrote {len(combined)} intervals.")


if __name__ == "__main__":
    main()
