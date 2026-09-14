import pytest
from smart_classroom_api.domain.reference_policy import Policy, energy_wh, saving_ratio


def occupied(p, now=0):
    p.motion(True, now)
    return p


def test_empty_loads_off():
    p = Policy()
    p.update(35, 0, 0)
    assert all(p.devices[n].state == "OFF" for n in ("ac", "fan", "lights"))


def test_hot_occupied_ac_on():
    p = occupied(Policy())
    p.update(30, 500, 0)
    assert p.devices["ac"].state == "ON"


def test_moderate_fan_on():
    p = occupied(Policy())
    p.update(26, 500, 0)
    assert p.devices["fan"].state == "ON"


def test_dark_lights_on():
    p = occupied(Policy())
    p.update(20, 100, 0)
    assert p.devices["lights"].state == "ON"


def test_bright_lights_off():
    p = occupied(Policy())
    p.update(20, 500, 0)
    assert p.devices["lights"].state == "OFF"


def test_ac_hysteresis():
    p = occupied(Policy())
    p.update(29, 500, 0)
    p.update(27, 500, 1)
    assert p.devices["ac"].state == "ON"


def test_fan_hysteresis():
    p = occupied(Policy())
    p.update(26, 500, 0)
    p.update(24, 500, 1)
    assert p.devices["fan"].state == "ON"


def test_occupancy_timeout():
    p = occupied(Policy())
    p.motion(False, 15000)
    assert not p.occupied


def test_motion_renews_timeout():
    p = occupied(Policy())
    p.motion(True, 10000)
    p.motion(False, 16000)
    assert p.occupied


def test_force_on():
    p = Policy()
    p.devices["ac"].override = "FORCE_ON"
    p.update(20, 500, 0)
    assert p.devices["ac"].state == "ON"


def test_force_off():
    p = occupied(Policy())
    p.devices["ac"].override = "FORCE_OFF"
    p.update(35, 500, 0)
    assert p.devices["ac"].state == "OFF"


def test_restore_auto():
    p = occupied(Policy())
    p.devices["ac"].override = "FORCE_OFF"
    p.devices["ac"].override = "AUTO"
    p.update(35, 500, 0)
    assert p.devices["ac"].state == "ON"


def test_projector_on():
    p = occupied(Policy())
    assert p.projector(True, 0) and p.devices["projector"].state == "ON"


def test_projector_shutdown_cools():
    p = occupied(Policy())
    p.projector(True, 0)
    p.projector(False, 100)
    assert p.devices["projector"].state == "COOLING_DOWN"


def test_projector_cooldown_off():
    p = occupied(Policy())
    p.projector(True, 0)
    p.projector(False, 100)
    p.update(20, 500, 8100)
    assert p.devices["projector"].state == "OFF"


def test_runtime_accumulation():
    p = occupied(Policy())
    p.update(30, 500, 0)
    p.devices["ac"].transition("OFF", 3600000)
    assert p.devices["ac"].runtime(3600000) == 3600000


def test_energy_calculation():
    assert energy_wh(1000, 3600000) == pytest.approx(1000)


def test_zero_baseline_guard():
    assert saving_ratio(0, 12) == 0


def test_saving_ratio():
    assert saving_ratio(100, 60) == pytest.approx(40)


def test_network_independent_local_policy():
    p = occupied(Policy())
    p.update(30, 100, 0)
    assert p.devices["ac"].state == p.devices["lights"].state == "ON"


def test_pending_off_cancelled():
    p = occupied(Policy())
    p.update(30, 500, 0)
    p.occupied = False
    p.update(30, 500, 1)
    p.occupied = True
    p.update(30, 500, 5000)
    assert p.devices["ac"].state == "ON" and p.devices["ac"].pending_since is None
