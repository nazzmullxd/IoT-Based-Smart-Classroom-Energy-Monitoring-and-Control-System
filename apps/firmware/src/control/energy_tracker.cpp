#include "smart_classroom/control/energy_tracker.h"

#include "smart_classroom/config.h"

float EnergyTracker::deviceWh(
    DeviceId id,
    const DeviceManager &devices,
    unsigned long now) {
  const float watts[] = {
      Config::AC_POWER_W,
      Config::FAN_POWER_W,
      Config::LIGHT_POWER_W,
      Config::PROJECTOR_POWER_W,
  };
  return watts[(int)id] * (devices.runtimeMs(id, now) / 3600000.0f);
}

float EnergyTracker::totalWh(const DeviceManager &devices, unsigned long now) {
  float total = 0;
  for (int i = 0; i < 4; i++) {
    total += deviceWh((DeviceId)i, devices, now);
  }
  return total;
}

float EnergyTracker::savingRatio(float conventional, float automated) {
  return conventional <= 0 ? 0.0f : (conventional - automated) / conventional * 100.0f;
}
