#include "smart_classroom/control/control_policy.h"

#include "smart_classroom/config.h"

bool ControlPolicy::desired(
    DeviceId id,
    const SensorReading &reading,
    const DeviceRecord &record,
    OperatingMode mode) const {
  if (record.overrideMode == OverrideMode::FORCE_ON) {
    return true;
  }
  if (record.overrideMode == OverrideMode::FORCE_OFF) {
    return false;
  }
  if (mode == OperatingMode::CONVENTIONAL) {
    return id != DeviceId::PROJECTOR;
  }
  if (id == DeviceId::PROJECTOR) {
    return record.state == DeviceState::ON;
  }
  if (!reading.occupied) {
    return false;
  }
  if (id == DeviceId::AC) {
    return record.state == DeviceState::ON
               ? reading.temperatureC > Config::AC_OFF_C
               : reading.temperatureC >= Config::AC_ON_C;
  }
  if (id == DeviceId::FAN) {
    return record.state == DeviceState::ON
               ? reading.temperatureC > Config::FAN_OFF_C
               : reading.temperatureC >= Config::FAN_ON_C;
  }
  return record.state == DeviceState::ON
             ? reading.illuminanceLux < Config::LIGHT_OFF_LUX
             : reading.illuminanceLux <= Config::LIGHT_ON_LUX;
}
