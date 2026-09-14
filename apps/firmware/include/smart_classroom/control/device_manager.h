#pragma once

#include "smart_classroom/control/control_policy.h"
#include "smart_classroom/models.h"

class DeviceManager {
 public:
  void begin();
  void update(const SensorReading &reading, OperatingMode mode, unsigned long now);
  bool setOverride(
      DeviceId id,
      OverrideMode mode,
      unsigned long now,
      const char *reason = "MANUAL_OVERRIDE");
  bool requestProjector(bool on, bool occupied, unsigned long now, const char *reason);
  DeviceRecord &record(DeviceId id) { return records_[(int)id]; }
  const DeviceRecord &record(DeviceId id) const { return records_[(int)id]; }
  uint64_t runtimeMs(DeviceId id, unsigned long now) const;
  void reset(unsigned long now);

 private:
  DeviceRecord records_[4];
  ControlPolicy policy_;
  void transition(DeviceId id, DeviceState state, unsigned long now, const char *reason);
  void applyDelayed(
      DeviceId id,
      bool desired,
      unsigned long delayMs,
      unsigned long now,
      const char *onReason);
  uint8_t pin(DeviceId id) const;
};
