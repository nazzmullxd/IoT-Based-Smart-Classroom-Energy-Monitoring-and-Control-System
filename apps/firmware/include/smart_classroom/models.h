#pragma once
#include <Arduino.h>

enum class DeviceId : uint8_t { AC, FAN, LIGHT, PROJECTOR };
enum class OverrideMode : uint8_t { AUTO, FORCE_ON, FORCE_OFF };
enum class OperatingMode : uint8_t { AUTO, CONVENTIONAL };
enum class DeviceState : uint8_t { OFF, ON, COOLING_DOWN };

struct SensorReading {
  unsigned long uptimeMs = 0;
  float temperatureC = NAN;
  float humidityPct = NAN;
  float illuminanceLux = 0;
  int ldrRaw = 0;
  bool occupied = false;
  bool pirRaw = false;
  bool dark = false;
  bool dhtError = true;
  bool ldrError = false;
};

struct DeviceRecord {
  DeviceState state = DeviceState::OFF;
  OverrideMode overrideMode = OverrideMode::AUTO;
  unsigned long onSinceMs = 0;
  uint64_t accumulatedMs = 0;
  uint32_t transitions = 0;
  unsigned long pendingOffSinceMs = 0;
  bool pendingOff = false;
  const char *reason = "BOOT";
};

const char *stateName(DeviceState value);
const char *overrideName(OverrideMode value);
const char *modeName(OperatingMode value);

