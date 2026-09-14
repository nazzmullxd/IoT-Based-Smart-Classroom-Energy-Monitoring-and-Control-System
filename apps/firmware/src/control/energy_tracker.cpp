#include "smart_classroom/control/energy_tracker.h"

#include "smart_classroom/config.h"

float EnergyTracker::deviceWh(
    DeviceId id,
    const DeviceManager &devices,
    unsigned long now) {
  const float watts[] = {
      Config::LIGHT_POWER_W,
      Config::FAN_POWER_W,
      Config::COOLING_POWER_W,
  };
  return watts[(int)id] * devices.runtimeMs(id, now) / 3600000.0f;
}

float EnergyTracker::totalWh(const DeviceManager &devices, unsigned long now) {
  float total = 0.0f;
  for (int i = 0; i < (int)DeviceId::COUNT; ++i) {
    total += deviceWh((DeviceId)i, devices, now);
  }
  return total;
}

float EnergyTracker::savingRatio(float conventional, float smart) {
  return conventional <= 0.0f
             ? 0.0f
             : (conventional - smart) / conventional * 100.0f;
}
