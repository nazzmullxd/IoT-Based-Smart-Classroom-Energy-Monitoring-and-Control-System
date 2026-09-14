#include "smart_classroom/connectivity/telemetry_manager.h"

#include <ArduinoJson.h>

#include "smart_classroom/control/energy_tracker.h"
#include "smart_classroom/config.h"

void TelemetryManager::publish(
    NetworkManager &network,
    const SensorReading &reading,
    const DeviceManager &devices,
    OperatingMode mode,
    unsigned long now) {
  JsonDocument document;
  document["deviceId"] = Config::DEVICE_ID;
  document["uptimeMs"] = now;
  document["temperatureC"] = reading.temperatureC;
  document["humidityPct"] = reading.humidityPct;
  document["illuminanceLux"] = reading.illuminanceLux;
  document["ldrRaw"] = reading.ldrRaw;
  document["occupied"] = reading.occupied;
  document["pirRaw"] = reading.pirRaw;
  document["dark"] = reading.dark;
  document["sensorError"] = reading.dhtError || reading.ldrError;
  document["mode"] = modeName(mode);

  const char *names[] = {"ac", "fan", "lights", "projector"};
  for (int i = 0; i < 4; i++) {
    auto id = (DeviceId)i;
    JsonObject device = document["devices"][names[i]].to<JsonObject>();
    device["state"] = stateName(devices.record(id).state);
    device["override"] = overrideName(devices.record(id).overrideMode);
    device["runtimeSeconds"] = devices.runtimeMs(id, now) / 1000;
    device["transitions"] = devices.record(id).transitions;
    device["reason"] = devices.record(id).reason;
    device["estimatedEnergyWh"] = EnergyTracker::deviceWh(id, devices, now);
  }

  document["estimatedEnergyWh"]["total"] = EnergyTracker::totalWh(devices, now);
  document["network"]["wifi"] = network.wifiConnected();
  document["network"]["mqtt"] = network.mqttConnected();

  char output[1900];
  size_t length = serializeJson(document, output, sizeof(output));
  if (length) {
    network.publish(Config::TOPIC_TELEMETRY, output);
  }
}
