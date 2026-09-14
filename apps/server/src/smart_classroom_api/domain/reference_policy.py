"""Hardware-independent reference policy used for automated verification."""

from dataclasses import dataclass, field


@dataclass
class Device:
    state: str = "OFF"
    override: str = "AUTO"
    runtime_ms: int = 0
    on_since: int | None = None
    pending_since: int | None = None

    def transition(self, state, now):
        if self.state == state:
            return
        if self.state == "OFF" and state != "OFF":
            self.on_since = now
        if self.state != "OFF" and state == "OFF" and self.on_since is not None:
            self.runtime_ms += now - self.on_since
            self.on_since = None
        self.state = state
        self.pending_since = None

    def runtime(self, now):
        return self.runtime_ms + (
            now - self.on_since
            if self.state != "OFF" and self.on_since is not None
            else 0
        )


@dataclass
class Policy:
    devices: dict = field(
        default_factory=lambda: {
            n: Device() for n in ("ac", "fan", "lights", "projector")
        }
    )
    occupied: bool = False
    last_motion: int | None = None
    mode: str = "AUTO"
    occupancy_hold: int = 15000
    cooldown: int = 8000

    def motion(self, active, now):
        if active:
            self.occupied = True
            self.last_motion = now
        elif (
            self.occupied
            and self.last_motion is not None
            and now - self.last_motion >= self.occupancy_hold
        ):
            self.occupied = False

    def desired(self, name, temp, lux):
        d = self.devices[name]
        if d.override == "FORCE_ON":
            return True
        if d.override == "FORCE_OFF":
            return False
        if self.mode == "CONVENTIONAL":
            return name != "projector"
        if not self.occupied:
            return False
        if name == "ac":
            return temp > (26 if d.state == "ON" else 27.999)
        if name == "fan":
            return temp > (23.5 if d.state == "ON" else 24.999)
        if name == "lights":
            return lux < (220 if d.state == "ON" else 150.001)
        return d.state == "ON"

    def update(self, temp, lux, now):
        for name, delay in (("ac", 6000), ("fan", 3000), ("lights", 5000)):
            d = self.devices[name]
            wanted = self.desired(name, temp, lux)
            if wanted:
                d.pending_since = None
                d.transition("ON", now)
            elif d.state != "OFF":
                if d.pending_since is None:
                    d.pending_since = now
                elif now - d.pending_since >= delay:
                    d.transition("OFF", now)
        p = self.devices["projector"]
        if p.override == "FORCE_ON" and p.state == "OFF":
            p.transition("ON", now)
        if (
            p.override == "FORCE_OFF" or (self.mode == "AUTO" and not self.occupied)
        ) and p.state == "ON":
            p.transition("COOLING_DOWN", now)
            p.pending_since = now
        if (
            p.state == "COOLING_DOWN"
            and p.pending_since is not None
            and now - p.pending_since >= self.cooldown
        ):
            p.transition("OFF", now)

    def projector(self, on, now):
        p = self.devices["projector"]
        if on and self.occupied and p.state == "OFF":
            p.transition("ON", now)
            return True
        if not on and p.state == "ON":
            p.transition("COOLING_DOWN", now)
            p.pending_since = now
            return True
        return False


def energy_wh(power_w, runtime_ms):
    return power_w * runtime_ms / 3_600_000


def saving_ratio(conventional, automated):
    return 0 if conventional <= 0 else (conventional - automated) / conventional * 100
