#pragma once

#include <Arduino.h>

class OccupancyManager {
 public:
  bool update(bool motion, unsigned long now);
  bool occupied() const { return occupied_; }

 private:
  bool occupied_ = false;
  bool everDetected_ = false;
  unsigned long lastMotionMs_ = 0;
};
