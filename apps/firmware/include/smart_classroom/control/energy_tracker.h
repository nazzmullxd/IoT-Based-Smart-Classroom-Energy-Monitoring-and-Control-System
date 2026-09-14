#pragma once

#include "smart_classroom/control/device_manager.h"

class EnergyTracker {
 public:
  static float deviceWh(DeviceId id, const DeviceManager &devices, unsigned long now);
  static float totalWh(const DeviceManager &devices, unsigned long now);
  static float savingRatio(float conventionalWh, float automatedWh);
};
