#pragma once

#include <Arduino.h>

enum class DeviceId : uint8_t { LIGHT = 0, FAN = 1, COOLING = 2, COUNT = 3 };
enum class OperatingMode : uint8_t { SMART, CONVENTIONAL, MANUAL };
enum class DeviceState : uint8_t { OFF, ON };

struct SensorReading {
  unsigned long uptimeMs = 0;
  float temperatureC = NAN;
  float humidityPct = NAN;
  float illuminanceLux = 0.0f;
  int ldrRaw = 0;
  bool occupied = false;
  bool pirRaw = false;
  bool sensorError = true;
};

struct DeviceRecord {
  DeviceState state = DeviceState::OFF;
  unsigned long onSinceMs = 0;
  uint64_t accumulatedMs = 0;
  uint32_t switchingEvents = 0;
  const char *reason = "BOOT";
};

const char *deviceName(DeviceId value);
const char *stateName(DeviceState value);
const char *modeName(OperatingMode value);
