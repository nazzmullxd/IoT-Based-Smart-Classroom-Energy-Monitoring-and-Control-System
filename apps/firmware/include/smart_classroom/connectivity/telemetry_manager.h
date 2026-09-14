#pragma once

#include "smart_classroom/control/device_manager.h"
#include "smart_classroom/connectivity/network_manager.h"
#include "smart_classroom/models.h"

class TelemetryManager {
 public:
  void publish(
      NetworkManager &network,
      const SensorReading &reading,
      const DeviceManager &devices,
      OperatingMode mode,
      unsigned long now);
};
