from dataclasses import dataclass, field

try:
    from . import config
except ImportError:  # Supports `python experiments/run_experiment.py`.
    import config


DEVICES = ("light", "fan", "cooling")


@dataclass
class ExperimentalController:
    strategy: str
    state: dict[str, bool] = field(
        default_factory=lambda: {name: False for name in DEVICES}
    )
    runtime_seconds: dict[str, float] = field(
        default_factory=lambda: {name: 0.0 for name in DEVICES}
    )
    energy_wh: dict[str, float] = field(
        default_factory=lambda: {name: 0.0 for name in DEVICES}
    )
    switches: dict[str, int] = field(
        default_factory=lambda: {name: 0 for name in DEVICES}
    )
    effective_occupancy: bool = False
    previous_actual_occupancy: bool = False
    vacancy_started_seconds: float | None = None
    activation_delays: list[float] = field(default_factory=list)
    shutdown_delays: list[float] = field(default_factory=list)

    def update_occupancy(self, actual: bool, now_seconds: float) -> None:
        if actual:
            if not self.previous_actual_occupancy:
                self.activation_delays.append(0.0)
            self.effective_occupancy = True
            self.vacancy_started_seconds = None
        elif self.previous_actual_occupancy:
            self.vacancy_started_seconds = now_seconds
        if (
            not actual
            and self.effective_occupancy
            and self.vacancy_started_seconds is not None
            and now_seconds - self.vacancy_started_seconds
            >= config.OCCUPANCY_TIMEOUT_SECONDS
        ):
            self.effective_occupancy = False
        self.previous_actual_occupancy = actual

    def occupancy_expiry(self) -> float | None:
        if self.effective_occupancy and self.vacancy_started_seconds is not None:
            return self.vacancy_started_seconds + config.OCCUPANCY_TIMEOUT_SECONDS
        return None

    def _temperature_desired(self, device: str, temperature_c: float) -> bool:
        if self.strategy == "SMART_NO_HYSTERESIS":
            threshold = 27.0 if device == "fan" else 28.5
            return temperature_c >= threshold
        if device == "fan":
            threshold = (
                config.FAN_OFF_TEMP_C if self.state[device] else config.FAN_ON_TEMP_C
            )
            return temperature_c > threshold if self.state[device] else temperature_c >= threshold
        threshold = (
            config.COOLING_OFF_TEMP_C
            if self.state[device]
            else config.COOLING_ON_TEMP_C
        )
        return temperature_c > threshold if self.state[device] else temperature_c >= threshold

    def _light_desired(self, lux: float) -> bool:
        if self.strategy == "SMART_NO_HYSTERESIS":
            return lux < 200.0
        threshold = config.LIGHT_OFF_LUX if self.state["light"] else config.LIGHT_ON_LUX
        return lux < threshold if self.state["light"] else lux <= threshold

    def desired(self, device: str, temperature_c: float, lux: float) -> bool:
        if self.strategy == "CONVENTIONAL":
            return True
        if not self.effective_occupancy:
            return False
        if self.strategy == "OCCUPANCY_ONLY":
            return True
        if device == "light":
            if self.strategy == "OCCUPANCY_TEMPERATURE":
                return True
            return self._light_desired(lux)
        if self.strategy == "OCCUPANCY_ILLUMINATION":
            return True
        return self._temperature_desired(device, temperature_c)

    def evaluate(
        self,
        actual_occupancy: bool,
        temperature_c: float,
        lux: float,
        now_seconds: float,
    ) -> dict[str, bool]:
        was_effectively_occupied = self.effective_occupancy
        self.update_occupancy(actual_occupancy, now_seconds)
        changes: dict[str, bool] = {}
        for device in DEVICES:
            wanted = self.desired(device, temperature_c, lux)
            if wanted != self.state[device]:
                self.state[device] = wanted
                self.switches[device] += 1
                changes[device] = wanted
        if was_effectively_occupied and not self.effective_occupancy:
            delay = now_seconds - (self.vacancy_started_seconds or now_seconds)
            self.shutdown_delays.append(delay)
        return changes

    def integrate(self, duration_seconds: float) -> tuple[dict[str, float], dict[str, float]]:
        runtimes: dict[str, float] = {}
        energies: dict[str, float] = {}
        for device in DEVICES:
            runtime = duration_seconds if self.state[device] else 0.0
            energy = config.POWERS_W[device] * runtime / 3600.0
            self.runtime_seconds[device] += runtime
            self.energy_wh[device] += energy
            runtimes[device] = runtime
            energies[device] = energy
        return runtimes, energies
