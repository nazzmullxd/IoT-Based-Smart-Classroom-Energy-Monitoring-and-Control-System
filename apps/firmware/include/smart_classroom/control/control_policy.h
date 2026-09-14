#pragma once

#include "smart_classroom/models.h"

class ControlPolicy {
 public:
  bool desired(
      DeviceId id,
      const SensorReading &reading,
      const DeviceRecord &record,
      OperatingMode mode) const;
};
