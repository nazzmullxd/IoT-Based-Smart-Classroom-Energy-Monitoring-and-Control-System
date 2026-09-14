#pragma once

#include "smart_classroom/control/control_policy.h"
#include "smart_classroom/models.h"

class DeviceManager {
 public:
  void begin();
  void update(const SensorReading &reading, OperatingMode mode, unsigned long now);
  bool setManual(DeviceId id, bool on, OperatingMode mode, unsigned long now);
  const DeviceRecord &record(DeviceId id) const { return records_[(int)id]; }
  uint64_t runtimeMs(DeviceId id, unsigned long now) const;
  void resetRuntime(unsigned long now);

 private:
  DeviceRecord records_[(int)DeviceId::COUNT];
  ControlPolicy policy_;
  uint8_t pin(DeviceId id) const;
  void transition(DeviceId id, bool on, unsigned long now, const char *reason);
};
