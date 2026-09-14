#include "smart_classroom/control/control_policy.h"

#include <math.h>

#include "smart_classroom/config.h"

bool ControlPolicy::desired(
    DeviceId id,
    const SensorReading &reading,
    const DeviceRecord &record,
    OperatingMode mode) const {
  if (mode == OperatingMode::MANUAL) {
    return record.state == DeviceState::ON;
  }
  if (mode == OperatingMode::CONVENTIONAL) {
    return true;  // Scheduled baseline: all loads remain on for the run.
  }
  if (!reading.occupied) {
    return false;
  }

  const bool currentlyOn = record.state == DeviceState::ON;
  if (id == DeviceId::LIGHT) {
    return currentlyOn
               ? reading.illuminanceLux < Config::LIGHT_OFF_LUX
               : reading.illuminanceLux <= Config::LIGHT_ON_LUX;
  }
  if (isnan(reading.temperatureC)) {
    return false;
  }
  if (id == DeviceId::FAN) {
    return currentlyOn
               ? reading.temperatureC > Config::FAN_OFF_TEMP_C
               : reading.temperatureC >= Config::FAN_ON_TEMP_C;
  }
  return currentlyOn
             ? reading.temperatureC > Config::COOLING_OFF_TEMP_C
             : reading.temperatureC >= Config::COOLING_ON_TEMP_C;
}
