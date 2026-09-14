#include "smart_classroom/connectivity/telemetry_manager.h"

#include <ArduinoJson.h>

#include "smart_classroom/config.h"
#include "smart_classroom/control/energy_tracker.h"

const String &TelemetryManager::bootId() {
  if (bootId_.length() == 0) {
    bootId_ = String("boot-") + String((uint32_t)ESP.getEfuseMac(), HEX) + "-" +
              String(millis(), HEX);
  }
  return bootId_;
}

void TelemetryManager::publish(
    NetworkManager &network,
    const SensorReading &reading,
    const DeviceManager &devices,
    OperatingMode mode,
    unsigned long now) {
  JsonDocument document;
  document["device_id"] = Config::DEVICE_ID;
  document["boot_id"] = bootId();
  document["sequence"] = ++sequence_;
  document["uptime_ms"] = now;
  document["occupancy"] = reading.occupied;
  document["temperature_c"] = reading.temperatureC;
  document["humidity_pct"] = reading.humidityPct;
  document["lux"] = reading.illuminanceLux;
  document["sensor_error"] = reading.sensorError;
  document["mode"] = modeName(mode);

  for (int i = 0; i < (int)DeviceId::COUNT; ++i) {
    const DeviceId id = (DeviceId)i;
    const char *name = deviceName(id);
    const auto &record = devices.record(id);
    document[name] = record.state == DeviceState::ON;
    document[String(name) + "_runtime_seconds"] = devices.runtimeMs(id, now) / 1000.0f;
    document[String(name) + "_switching_events"] = record.switchingEvents;
    document[String(name) + "_energy_wh"] = EnergyTracker::deviceWh(id, devices, now);
  }
  document["estimated_energy_wh"] = EnergyTracker::totalWh(devices, now);
  document["mqtt_connected"] = network.mqttConnected();

  char output[1024];
  const size_t length = serializeJson(document, output, sizeof(output));
  if (length) network.publish(Config::TOPIC_TELEMETRY, output);
}
