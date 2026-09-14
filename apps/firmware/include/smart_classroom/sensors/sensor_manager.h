#pragma once

#include <DHT.h>

#include "smart_classroom/models.h"

class SensorManager {
 public:
  SensorManager();
  void begin();
  bool update(unsigned long now, bool occupied);
  const SensorReading &reading() const { return reading_; }

 private:
  DHT dht_;
  SensorReading reading_;
  unsigned long lastReadMs_ = 0;
  float rawToLux(int raw, bool &error);
};
