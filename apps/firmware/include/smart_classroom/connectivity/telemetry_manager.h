#pragma once

#include <Arduino.h>

#include "smart_classroom/control/device_manager.h"
#include "smart_classroom/connectivity/network_manager.h"
#include "smart_classroom/models.h"

class TelemetryManager {
 public:
  void publish(
      ClassroomNetwork &network,
      const SensorReading &reading,
      const DeviceManager &devices,
      OperatingMode mode,
      unsigned long now);

 private:
  String bootId_;
  uint32_t sequence_ = 0;
  const String &bootId();
};
