#include <Arduino.h>
#include <ArduinoJson.h>

#include "smart_classroom/config.h"
#include "smart_classroom/control/device_manager.h"
#include "smart_classroom/control/energy_tracker.h"
#include "smart_classroom/connectivity/network_manager.h"
#include "smart_classroom/connectivity/telemetry_manager.h"
#include "smart_classroom/sensors/occupancy_manager.h"
#include "smart_classroom/sensors/sensor_manager.h"

SensorManager sensors;
OccupancyManager occupancy;
DeviceManager devices;
NetworkManager network;
TelemetryManager telemetry;
OperatingMode operatingMode = OperatingMode::AUTO;

unsigned long lastTelemetry = 0;
unsigned long lastStatus = 0;
unsigned long lastButton = 0;
bool lastButtonState = HIGH;
String serialLine;

void printStatus(unsigned long now);

bool parseDevice(const String &value, DeviceId &device) {
  if (value == "AC") {
    device = DeviceId::AC;
  } else if (value == "FAN") {
    device = DeviceId::FAN;
  } else if (value == "LIGHT" || value == "LIGHTS") {
    device = DeviceId::LIGHT;
  } else if (value == "PROJECTOR") {
    device = DeviceId::PROJECTOR;
  } else {
    return false;
  }
  return true;
}

void applyCommand(String line, const char *source) {
  line.trim();
  line.toUpperCase();

  if (line == "STATUS") {
    printStatus(millis());
    return;
  }
  if (line == "HELP") {
    Serial.println(
        "STATUS | MODE AUTO|CONVENTIONAL | "
        "AC|FAN|LIGHT|PROJECTOR AUTO|ON|OFF | RESET ENERGY|RUNTIME");
    return;
  }
  if (line == "RESET ENERGY" || line == "RESET RUNTIME" || line == "RESET ALL") {
    devices.reset(millis());
    return;
  }
  if (line.startsWith("MODE ")) {
    operatingMode = line.endsWith("CONVENTIONAL")
                        ? OperatingMode::CONVENTIONAL
                        : OperatingMode::AUTO;
    Serial.printf("[EVENT] mode=%s source=%s\n", modeName(operatingMode), source);
    return;
  }

  int separator = line.indexOf(' ');
  if (separator < 1) {
    Serial.println("[ERROR] malformed command");
    return;
  }

  DeviceId id;
  if (!parseDevice(line.substring(0, separator), id)) {
    Serial.println("[ERROR] unknown device");
    return;
  }

  String command = line.substring(separator + 1);
  if (command == "AUTO") {
    devices.setOverride(id, OverrideMode::AUTO, millis());
  } else if (command == "ON" || command == "FORCE_ON") {
    devices.setOverride(id, OverrideMode::FORCE_ON, millis());
    if (id == DeviceId::PROJECTOR) {
      devices.requestProjector(true, sensors.reading().occupied, millis(), "MANUAL_REQUEST");
    }
  } else if (command == "OFF" || command == "FORCE_OFF") {
    devices.setOverride(id, OverrideMode::FORCE_OFF, millis());
    if (id == DeviceId::PROJECTOR) {
      devices.requestProjector(false, sensors.reading().occupied, millis(), "MANUAL_REQUEST");
    }
  } else {
    Serial.println("[ERROR] invalid command");
  }
}

void mqttCommand(const char *payload) {
  JsonDocument document;
  if (deserializeJson(document, payload)) {
    Serial.println("[ERROR] malformed MQTT JSON");
    return;
  }

  String command = document["command"] | "";
  String device = document["device"] | "";
  String value = document["value"] | "";

  if (command == "mode") {
    applyCommand("MODE " + value, "MQTT");
  } else if (command == "reset") {
    applyCommand("RESET " + value, "MQTT");
  } else if (command == "override") {
    applyCommand(device + " " + value, "MQTT");
  } else {
    Serial.println("[ERROR] unknown MQTT command");
  }
}

void printStatus(unsigned long now) {
  const auto &reading = sensors.reading();
  Serial.printf(
      "\nSMART CLASSROOM STATUS\n"
      "Temp: %.1f C  Humidity: %.1f %%  Lux: %.1f  Occupancy: %s\n",
      reading.temperatureC,
      reading.humidityPct,
      reading.illuminanceLux,
      reading.occupied ? "OCCUPIED" : "EMPTY");
  Serial.printf(
      "AC:%s Fan:%s Light:%s Projector:%s Mode:%s\n",
      stateName(devices.record(DeviceId::AC).state),
      stateName(devices.record(DeviceId::FAN).state),
      stateName(devices.record(DeviceId::LIGHT).state),
      stateName(devices.record(DeviceId::PROJECTOR).state),
      modeName(operatingMode));
  Serial.printf(
      "Estimated Energy: %.3f Wh WiFi:%s MQTT:%s\n",
      EnergyTracker::totalWh(devices, now),
      network.wifiConnected() ? "CONNECTED" : "OFFLINE",
      network.mqttConnected() ? "CONNECTED" : "OFFLINE");
}

void setup() {
  Serial.begin(115200);
  pinMode(Config::PIR_PIN, INPUT);
  pinMode(Config::PROJECTOR_BUTTON_PIN, INPUT_PULLUP);
  devices.begin();
  sensors.begin();
  network.begin(mqttCommand);
  Serial.println("Smart Classroom controller ready. Type HELP for commands.");
}

void loop() {
  unsigned long now = millis();
  bool pir = digitalRead(Config::PIR_PIN);
  bool occupiedNow = occupancy.update(pir, now);

  sensors.update(now, occupiedNow);
  devices.update(sensors.reading(), operatingMode, now);

  bool buttonState = digitalRead(Config::PROJECTOR_BUTTON_PIN);
  if (buttonState != lastButtonState &&
      (unsigned long)(now - lastButton) > Config::BUTTON_DEBOUNCE_MS) {
    lastButton = now;
    lastButtonState = buttonState;
    if (buttonState == LOW) {
      devices.requestProjector(
          devices.record(DeviceId::PROJECTOR).state == DeviceState::OFF,
          occupiedNow,
          now,
          "BUTTON");
    }
  }

  while (Serial.available()) {
    char character = Serial.read();
    if (character == '\n') {
      applyCommand(serialLine, "SERIAL");
      serialLine = "";
    } else if (character != '\r' && serialLine.length() < 100) {
      serialLine += character;
    }
  }

  network.loop(now);

  if ((unsigned long)(now - lastTelemetry) >= Config::TELEMETRY_INTERVAL_MS) {
    lastTelemetry = now;
    telemetry.publish(network, sensors.reading(), devices, operatingMode, now);
  }
  if ((unsigned long)(now - lastStatus) >= Config::STATUS_INTERVAL_MS) {
    lastStatus = now;
    printStatus(now);
  }

  delay(2);
}
