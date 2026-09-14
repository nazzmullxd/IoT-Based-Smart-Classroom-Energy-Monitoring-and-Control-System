from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
DEVICES = ("light", "fan", "cooling")


def aggregate(data: pd.DataFrame) -> pd.DataFrame:
    aggregations = {
        "estimated_energy_wh": "sum",
        "switching_events": "sum",
        "activation_events": "sum",
        "activation_delay_seconds": "sum",
        "shutdown_events": "sum",
        "shutdown_delay_seconds": "sum",
        "duration_seconds": "sum",
        "occupied_seconds": "sum",
        "sufficient_illumination_seconds": "sum",
        "thermal_comfort_seconds": "sum",
        "thermal_demand_seconds": "sum",
        "thermal_response_seconds": "sum",
    }
    for device in DEVICES:
        aggregations[f"{device}_runtime_seconds"] = "sum"
        aggregations[f"{device}_energy_wh"] = "sum"
    summary = data.groupby(["scenario", "mode"], as_index=False).agg(aggregations)
    summary["sufficient_illumination_pct"] = np.where(
        summary.occupied_seconds > 0,
        summary.sufficient_illumination_seconds / summary.occupied_seconds * 100,
        100,
    )
    summary["thermal_comfort_pct"] = np.where(
        summary.occupied_seconds > 0,
        summary.thermal_comfort_seconds / summary.occupied_seconds * 100,
        100,
    )
    summary["thermal_response_pct"] = np.where(
        summary.thermal_demand_seconds > 0,
        summary.thermal_response_seconds / summary.thermal_demand_seconds * 100,
        100,
    )
    summary["average_activation_delay_seconds"] = np.where(
        summary.activation_events > 0,
        summary.activation_delay_seconds / summary.activation_events,
        0,
    )
    summary["average_shutdown_delay_seconds"] = np.where(
        summary.shutdown_events > 0,
        summary.shutdown_delay_seconds / summary.shutdown_events,
        0,
    )
    return summary


def publication_style() -> None:
    plt.rcParams.update({
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "figure.dpi": 160,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "axes.spines.top": False,
        "axes.spines.right": False,
    })


def save_figure(name: str) -> None:
    plt.tight_layout()
    plt.savefig(FIGURES / name, bbox_inches="tight")
    plt.close()


def main() -> None:
    data = pd.read_csv(RESULTS / "combined_results.csv")
    summary = aggregate(data)
    summary.to_csv(RESULTS / "energy_by_scenario.csv", index=False)

    runtime = summary.melt(
        id_vars=["scenario", "mode"],
        value_vars=[f"{device}_runtime_seconds" for device in DEVICES],
        var_name="device",
        value_name="runtime_seconds",
    )
    runtime["device"] = runtime.device.str.replace("_runtime_seconds", "", regex=False)
    runtime.to_csv(RESULTS / "runtime_comparison.csv", index=False)

    comparison = summary[summary["mode"].isin(["SMART", "CONVENTIONAL"])].pivot(
        index="scenario", columns="mode", values="estimated_energy_wh"
    ).reset_index()
    comparison["estimated_saving_wh"] = comparison["CONVENTIONAL"] - comparison["SMART"]
    comparison["estimated_saving_pct"] = np.where(
        comparison["CONVENTIONAL"] > 0,
        comparison["estimated_saving_wh"] / comparison["CONVENTIONAL"] * 100,
        0,
    )
    comparison.to_csv(RESULTS / "saving_summary.csv", index=False)

    FIGURES.mkdir(parents=True, exist_ok=True)
    publication_style()
    labels = comparison.scenario.str.replace("_", " ").str.title()
    x = np.arange(len(labels))

    plt.figure(figsize=(9, 4.5))
    plt.bar(x - .2, comparison["SMART"], .4, label="SMART", color="#1f5b83")
    plt.bar(x + .2, comparison["CONVENTIONAL"], .4, label="CONVENTIONAL", color="#8b96a5")
    plt.xticks(x, labels, rotation=25, ha="right")
    plt.ylabel("Estimated energy (Wh)")
    plt.legend(frameon=False)
    save_figure("smart_vs_conventional_energy.png")

    plt.figure(figsize=(9, 4.5))
    plt.bar(x, comparison.estimated_saving_pct, color="#39785d")
    plt.axhline(0, color="#303846", linewidth=.8)
    plt.xticks(x, labels, rotation=25, ha="right")
    plt.ylabel("Estimated energy saving (%)")
    save_figure("energy_saving_percentage.png")

    selected_runtime = runtime[runtime["mode"].isin(["SMART", "CONVENTIONAL"])]
    device_runtime = (
        selected_runtime.groupby(["mode", "device"])
        .runtime_seconds.sum()
        .unstack(0)
        .reindex(DEVICES)
        / 3600
    )
    device_runtime.plot(kind="bar", color=["#8b96a5", "#1f5b83"], figsize=(7, 4))
    plt.ylabel("Runtime across scenarios (h)")
    plt.xlabel("Device")
    plt.legend(frameon=False)
    save_figure("device_runtime_comparison.png")

    cumulative = data[
        (data.scenario == data.scenario.iloc[0])
        & data["mode"].isin(["SMART", "CONVENTIONAL"])
    ].copy()
    cumulative["elapsed_hours"] = cumulative.groupby("mode").duration_seconds.cumsum() / 3600
    cumulative["cumulative_wh"] = cumulative.groupby("mode").estimated_energy_wh.cumsum()
    plt.figure(figsize=(7, 4))
    for mode, rows in cumulative.groupby("mode"):
        plt.step(rows.elapsed_hours, rows.cumulative_wh, where="post", label=mode)
    plt.xlabel("Scenario elapsed time (h)")
    plt.ylabel("Cumulative estimated energy (Wh)")
    plt.legend(frameon=False)
    save_figure("energy_over_time.png")

    switches = summary[summary["mode"].isin(["SMART", "CONVENTIONAL"])].pivot(
        index="scenario", columns="mode", values="switching_events"
    )
    switches.plot(kind="bar", color=["#8b96a5", "#1f5b83"], figsize=(9, 4.5))
    plt.ylabel("Switching events")
    plt.xlabel("Scenario")
    plt.xticks(
        range(len(switches.index)),
        [name.replace("_", " ").title() for name in switches.index],
        rotation=25,
        ha="right",
    )
    plt.legend(frameon=False)
    save_figure("switching_frequency.png")

    print(f"Analyzed {len(comparison)} paired scenarios. Outputs: {RESULTS} and {FIGURES}")


if __name__ == "__main__":
    main()
