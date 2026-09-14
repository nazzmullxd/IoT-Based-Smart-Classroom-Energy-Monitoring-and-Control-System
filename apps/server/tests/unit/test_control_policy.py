import pytest

from experiments.controller import ExperimentalController
from smart_classroom_api.energy import energy_wh, saving_percentage


def evaluate(controller, occupied=True, temperature=25, lux=500, now=0):
    controller.evaluate(occupied, temperature, lux, now)
    return controller


def test_lighting_threshold_and_hysteresis():
    controller = evaluate(ExperimentalController("SMART"), lux=140)
    assert controller.state["light"] is True
    evaluate(controller, lux=200, now=1)
    assert controller.state["light"] is True
    evaluate(controller, lux=260, now=2)
    assert controller.state["light"] is False


def test_temperature_thresholds_and_hysteresis():
    controller = evaluate(ExperimentalController("SMART"), temperature=29)
    assert controller.state["fan"] is True
    assert controller.state["cooling"] is True
    evaluate(controller, temperature=28.5, now=1)
    assert controller.state["fan"] is True
    assert controller.state["cooling"] is True
    evaluate(controller, temperature=26, now=2)
    assert controller.state["fan"] is False
    assert controller.state["cooling"] is False


def test_occupancy_timeout_delays_shutdown():
    controller = evaluate(ExperimentalController("SMART"), temperature=30, lux=100)
    evaluate(controller, occupied=False, temperature=30, lux=100, now=1)
    assert all(controller.state.values())
    evaluate(controller, occupied=False, temperature=30, lux=100, now=601)
    assert not any(controller.state.values())


def test_conventional_mode_ignores_environment_and_vacancy():
    controller = evaluate(
        ExperimentalController("CONVENTIONAL"),
        occupied=False,
        temperature=20,
        lux=1000,
    )
    assert all(controller.state.values())


def test_smart_mode_keeps_empty_room_off():
    controller = evaluate(
        ExperimentalController("SMART"), occupied=False, temperature=35, lux=20
    )
    assert not any(controller.state.values())


def test_energy_equation_and_saving_guard():
    assert energy_wh(1000, 3600) == pytest.approx(1000)
    assert saving_percentage(100, 60) == pytest.approx(40)
    assert saving_percentage(0, 10) == 0
