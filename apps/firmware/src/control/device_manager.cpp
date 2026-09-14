#include "smart_classroom/control/device_manager.h"

#include "smart_classroom/config.h"

const char *deviceName(DeviceId value) {
  const char *names[] = {"light", "fan", "cooling"};
  return names[(int)value];
}

const char *stateName(DeviceState value) {
  return value == DeviceState::ON ? "ON" : "OFF";
}

const char *modeName(OperatingMode value) {
  if (value == OperatingMode::CONVENTIONAL) return "CONVENTIONAL";
  if (value == OperatingMode::MANUAL) return "MANUAL";
  return "SMART";
}

uint8_t DeviceManager::pin(DeviceId id) const {
  const uint8_t pins[] = {
      Config::LIGHT_RELAY_PIN,
      Config::FAN_RELAY_PIN,
      Config::COOLING_RELAY_PIN,
  };
  return pins[(int)id];
}

void DeviceManager::begin() {
  for (int i = 0; i < (int)DeviceId::COUNT; ++i) {
    pinMode(pin((DeviceId)i), OUTPUT);
    digitalWrite(pin((DeviceId)i), !Config::RELAY_ACTIVE_HIGH);
  }
}

void DeviceManager::transition(
    DeviceId id,
    bool on,
    unsigned long now,
    const char *reason) {
  auto &device = records_[(int)id];
  const DeviceState next = on ? DeviceState::ON : DeviceState::OFF;
  if (device.state == next) return;

  if (next == DeviceState::ON) {
    device.onSinceMs = now;
  } else {
    device.accumulatedMs += (unsigned long)(now - device.onSinceMs);
  }
  device.state = next;
  device.switchingEvents++;
  device.reason = reason;
  digitalWrite(pin(id), on == Config::RELAY_ACTIVE_HIGH);
  Serial.printf("[CONTROL] %s=%s reason=%s\n", deviceName(id), stateName(next), reason);
}

void DeviceManager::update(
    const SensorReading &reading,
    OperatingMode mode,
    unsigned long now) {
  for (int i = 0; i < (int)DeviceId::COUNT; ++i) {
    const DeviceId id = (DeviceId)i;
    const bool wanted = policy_.desired(id, reading, records_[i], mode);
    const char *reason = mode == OperatingMode::CONVENTIONAL
                             ? "SCHEDULED_BASELINE"
                             : (!reading.occupied ? "OCCUPANCY_TIMEOUT" : "SMART_POLICY");
    transition(id, wanted, now, reason);
  }
}

bool DeviceManager::setManual(
    DeviceId id,
    bool on,
    OperatingMode mode,
    unsigned long now) {
  if (mode != OperatingMode::MANUAL) return false;
  transition(id, on, now, "MANUAL_COMMAND");
  return true;
}

uint64_t DeviceManager::runtimeMs(DeviceId id, unsigned long now) const {
  const auto &device = records_[(int)id];
  return device.accumulatedMs +
         (device.state == DeviceState::ON
              ? (unsigned long)(now - device.onSinceMs)
              : 0);
}

void DeviceManager::resetRuntime(unsigned long now) {
  for (int i = 0; i < (int)DeviceId::COUNT; ++i) {
    records_[i].accumulatedMs = 0;
    records_[i].switchingEvents = 0;
    if (records_[i].state == DeviceState::ON) records_[i].onSinceMs = now;
  }
}
