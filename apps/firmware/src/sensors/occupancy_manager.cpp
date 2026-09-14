#include "smart_classroom/sensors/occupancy_manager.h"

#include "smart_classroom/config.h"

bool OccupancyManager::update(bool motion, unsigned long now) {
  if (motion) {
    lastMotionMs_ = now;
    everDetected_ = true;
    occupied_ = true;
  } else if (
      occupied_ &&
      everDetected_ &&
      (unsigned long)(now - lastMotionMs_) >= Config::OCCUPANCY_TIMEOUT_MS) {
    occupied_ = false;
  }
  return occupied_;
}
