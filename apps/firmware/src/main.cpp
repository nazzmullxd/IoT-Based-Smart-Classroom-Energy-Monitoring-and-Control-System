#include <Arduino.h>
#include <ArduinoJson.h>

#include "smart_classroom/config.h"
#include "smart_classroom/connectivity/network_manager.h"
#include "smart_classroom/connectivity/telemetry_manager.h"
#include "smart_classroom/control/device_manager.h"
#include "smart_classroom/control/energy_tracker.h"
#include "smart_classroom/sensors/occupancy_manager.h"
#include "smart_classroom/sensors/sensor_manager.h"

SensorManager sensors;
OccupancyManager occupancy;
DeviceManager devices;
ClassroomNetwork network;
TelemetryManager telemetry;
OperatingMode operatingMode = OperatingMode::SMART;

unsigned long lastTelemetryMs = 0;
unsigned long lastStatusMs = 0;

bool parseMode(const String &value, OperatingMode &mode) {
  if (value == "SMART") mode = OperatingMode::SMART;
  else if (value == "CONVENTIONAL") mode = OperatingMode::CONVENTIONAL;
  else if (value == "MANUAL") mode = OperatingMode::MANUAL;
  else return false;
  return true;
}

bool parseDevice(const String &value, DeviceId &id) {
  if (value == "light") id = DeviceId::LIGHT;
  else if (value == "fan") id = DeviceId::FAN;
  else if (value == "cooling") id = DeviceId::COOLING;
  else return false;
  return true;
}

void mqttCommand(const char *topic, const char *payload) {
  JsonDocument document;
  if (deserializeJson(document, payload)) {
    Serial.println("[COMMAND] rejected malformed JSON");
    return;
  }

  if (strcmp(topic, Config::TOPIC_MODE) == 0) {
    String value = document["mode"] | "";
    value.toUpperCase();
    OperatingMode requested;
    if (parseMode(value, requested)) {
      operatingMode = requested;
      Serial.printf("[COMMAND] mode=%s\n", modeName(operatingMode));
    }
    return;
  }

  String deviceValue = document["device"] | "";
  DeviceId id;
  if (!parseDevice(deviceValue, id) || !document["state"].is<bool>()) {
    Serial.println("[COMMAND] rejected invalid manual control");
    return;
  }
  if (!devices.setManual(id, document["state"].as<bool>(), operatingMode, millis())) {
    Serial.println("[COMMAND] select MANUAL mode before direct control");
  }
}

void printStatus(unsigned long now) {
  const auto &reading = sensors.reading();
  Serial.printf(
      "[STATUS] mode=%s occupancy=%s temp=%.1fC lux=%.0f ",
      modeName(operatingMode),
      reading.occupied ? "OCCUPIED" : "UNOCCUPIED",
      reading.temperatureC,
      reading.illuminanceLux);
  for (int i = 0; i < (int)DeviceId::COUNT; ++i) {
    const DeviceId id = (DeviceId)i;
    Serial.printf("%s=%s ", deviceName(id), stateName(devices.record(id).state));
  }
  Serial.printf(
      "estimated_energy=%.3fWh mqtt=%s\n",
      EnergyTracker::totalWh(devices, now),
      network.mqttConnected() ? "CONNECTED" : "OFFLINE");
}

void setup() {
  Serial.begin(115200);
  pinMode(Config::PIR_PIN, INPUT);
  devices.begin();
  sensors.begin();
  network.begin(mqttCommand);
  Serial.println("Smart Classroom thesis controller ready");
}

void loop() {
  const unsigned long now = millis();
  const bool occupiedNow = occupancy.update(digitalRead(Config::PIR_PIN), now);
  sensors.update(now, occupiedNow);
  devices.update(sensors.reading(), operatingMode, now);
  network.loop(now);

  if ((unsigned long)(now - lastTelemetryMs) >= Config::TELEMETRY_INTERVAL_MS) {
    lastTelemetryMs = now;
    telemetry.publish(network, sensors.reading(), devices, operatingMode, now);
  }
  if ((unsigned long)(now - lastStatusMs) >= Config::STATUS_INTERVAL_MS) {
    lastStatusMs = now;
    printStatus(now);
  }
  delay(2);
}
