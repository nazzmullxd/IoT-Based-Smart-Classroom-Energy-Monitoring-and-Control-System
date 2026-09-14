#include "smart_classroom/control/device_manager.h"

#include "smart_classroom/config.h"

const char *stateName(DeviceState value) {
  return value == DeviceState::ON
             ? "ON"
             : value == DeviceState::COOLING_DOWN ? "COOLING_DOWN" : "OFF";
}

const char *overrideName(OverrideMode value) {
  return value == OverrideMode::FORCE_ON
             ? "FORCE_ON"
             : value == OverrideMode::FORCE_OFF ? "FORCE_OFF" : "AUTO";
}

const char *modeName(OperatingMode value) {
  return value == OperatingMode::CONVENTIONAL ? "CONVENTIONAL" : "AUTO";
}

uint8_t DeviceManager::pin(DeviceId id) const {
  const uint8_t pins[] = {
      Config::AC_RELAY_PIN,
      Config::FAN_RELAY_PIN,
      Config::LIGHT_RELAY_PIN,
      Config::PROJECTOR_RELAY_PIN,
  };
  return pins[(int)id];
}

void DeviceManager::begin() {
  for (int i = 0; i < 4; i++) {
    pinMode(pin((DeviceId)i), OUTPUT);
    digitalWrite(pin((DeviceId)i), !Config::RELAY_ACTIVE_HIGH);
  }
}

uint64_t DeviceManager::runtimeMs(DeviceId id, unsigned long now) const {
  const auto &device = record(id);
  return device.accumulatedMs +
         (device.state != DeviceState::OFF ? (unsigned long)(now - device.onSinceMs) : 0);
}

void DeviceManager::transition(
    DeviceId id,
    DeviceState state,
    unsigned long now,
    const char *reason) {
  auto &device = record(id);
  if (device.state == state) {
    return;
  }

  if (device.state == DeviceState::OFF && state != DeviceState::OFF) {
    device.onSinceMs = now;
  }
  if (device.state != DeviceState::OFF && state == DeviceState::OFF) {
    device.accumulatedMs += (unsigned long)(now - device.onSinceMs);
  }

  device.state = state;
  device.transitions++;
  device.reason = reason;
  device.pendingOff = false;
  if (state == DeviceState::COOLING_DOWN) {
    device.pendingOff = true;
    device.pendingOffSinceMs = now;
  }

  digitalWrite(
      pin(id),
      state == DeviceState::OFF ? !Config::RELAY_ACTIVE_HIGH : Config::RELAY_ACTIVE_HIGH);
  Serial.printf("[EVENT] device=%d state=%s reason=%s\n", (int)id, stateName(state), reason);
}

void DeviceManager::applyDelayed(
    DeviceId id,
    bool desired,
    unsigned long delayMs,
    unsigned long now,
    const char *onReason) {
  auto &device = record(id);
  if (desired) {
    device.pendingOff = false;
    transition(id, DeviceState::ON, now, onReason);
    return;
  }
  if (device.state == DeviceState::OFF) {
    return;
  }
  if (!device.pendingOff) {
    device.pendingOff = true;
    device.pendingOffSinceMs = now;
    Serial.printf("[EVENT] device=%d pending_off delay_ms=%lu\n", (int)id, delayMs);
  } else if ((unsigned long)(now - device.pendingOffSinceMs) >= delayMs) {
    transition(id, DeviceState::OFF, now, "POLICY_OFF");
  }
}

void DeviceManager::update(
    const SensorReading &reading,
    OperatingMode mode,
    unsigned long now) {
  applyDelayed(
      DeviceId::AC,
      policy_.desired(DeviceId::AC, reading, record(DeviceId::AC), mode),
      Config::AC_OFF_DELAY_MS,
      now,
      "TEMP_HIGH");
  applyDelayed(
      DeviceId::FAN,
      policy_.desired(DeviceId::FAN, reading, record(DeviceId::FAN), mode),
      Config::FAN_OFF_DELAY_MS,
      now,
      "TEMP_THRESHOLD");
  applyDelayed(
      DeviceId::LIGHT,
      policy_.desired(DeviceId::LIGHT, reading, record(DeviceId::LIGHT), mode),
      Config::LIGHT_OFF_DELAY_MS,
      now,
      "OCCUPIED_DARK");

  auto &projector = record(DeviceId::PROJECTOR);
  if (projector.overrideMode == OverrideMode::FORCE_ON &&
      projector.state == DeviceState::OFF) {
    transition(DeviceId::PROJECTOR, DeviceState::ON, now, "MANUAL_OVERRIDE");
  }
  if ((projector.overrideMode == OverrideMode::FORCE_OFF ||
       (!reading.occupied && mode == OperatingMode::AUTO)) &&
      projector.state == DeviceState::ON) {
    transition(
        DeviceId::PROJECTOR,
        DeviceState::COOLING_DOWN,
        now,
        "CONTROLLED_SHUTDOWN");
  }
  if (projector.state == DeviceState::COOLING_DOWN &&
      projector.pendingOff &&
      (unsigned long)(now - projector.pendingOffSinceMs) >= Config::PROJECTOR_COOLDOWN_MS) {
    transition(DeviceId::PROJECTOR, DeviceState::OFF, now, "COOLDOWN_COMPLETE");
  }
}

bool DeviceManager::setOverride(
    DeviceId id,
    OverrideMode mode,
    unsigned long now,
    const char *reason) {
  record(id).overrideMode = mode;
  if (id == DeviceId::PROJECTOR &&
      mode == OverrideMode::FORCE_OFF &&
      record(id).state == DeviceState::ON) {
    transition(id, DeviceState::COOLING_DOWN, now, reason);
  }
  Serial.printf("[EVENT] override device=%d mode=%s\n", (int)id, overrideName(mode));
  return true;
}

bool DeviceManager::requestProjector(
    bool on,
    bool occupied,
    unsigned long now,
    const char *reason) {
  auto &projector = record(DeviceId::PROJECTOR);
  if (on) {
    if (!occupied && projector.overrideMode != OverrideMode::FORCE_ON) {
      return false;
    }
    if (projector.state == DeviceState::COOLING_DOWN) {
      return false;
    }
    transition(DeviceId::PROJECTOR, DeviceState::ON, now, reason);
  } else if (projector.state == DeviceState::ON) {
    transition(DeviceId::PROJECTOR, DeviceState::COOLING_DOWN, now, reason);
  }
  return true;
}

void DeviceManager::reset(unsigned long now) {
  for (int i = 0; i < 4; i++) {
    auto &device = records_[i];
    device.accumulatedMs = 0;
    device.transitions = 0;
    if (device.state != DeviceState::OFF) {
      device.onSinceMs = now;
    }
  }
}
