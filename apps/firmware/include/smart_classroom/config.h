#pragma once
#include <Arduino.h>

namespace Config {
constexpr bool SIMULATION_MODE = true;
constexpr uint8_t DHT_PIN = 15, PIR_PIN = 13, LDR_PIN = 34;
constexpr uint8_t AC_RELAY_PIN = 23, FAN_RELAY_PIN = 22;
constexpr uint8_t LIGHT_RELAY_PIN = 21, PROJECTOR_RELAY_PIN = 19;
constexpr uint8_t PROJECTOR_BUTTON_PIN = 27;
constexpr bool RELAY_ACTIVE_HIGH = true;

constexpr unsigned long SENSOR_INTERVAL_MS = 2000;
constexpr unsigned long TELEMETRY_INTERVAL_MS = 3000;
constexpr unsigned long STATUS_INTERVAL_MS = 5000;
constexpr unsigned long WIFI_RETRY_MS = 10000;
constexpr unsigned long MQTT_RETRY_MS = 5000;
constexpr unsigned long OCCUPANCY_HOLD_MS = SIMULATION_MODE ? 15000 : 900000;
constexpr unsigned long AC_OFF_DELAY_MS = SIMULATION_MODE ? 6000 : 300000;
constexpr unsigned long FAN_OFF_DELAY_MS = SIMULATION_MODE ? 3000 : 60000;
constexpr unsigned long LIGHT_OFF_DELAY_MS = SIMULATION_MODE ? 5000 : 180000;
constexpr unsigned long PROJECTOR_COOLDOWN_MS = SIMULATION_MODE ? 8000 : 120000;
constexpr unsigned long BUTTON_DEBOUNCE_MS = 60;

constexpr float AC_ON_C = 28.0f, AC_OFF_C = 26.0f;
constexpr float FAN_ON_C = 25.0f, FAN_OFF_C = 23.5f;
constexpr float LIGHT_ON_LUX = 150.0f, LIGHT_OFF_LUX = 220.0f;
constexpr float AC_POWER_W = 1500.0f, FAN_POWER_W = 75.0f;
constexpr float LIGHT_POWER_W = 120.0f, PROJECTOR_POWER_W = 300.0f;

constexpr char WIFI_SSID[] = "Wokwi-GUEST";
constexpr char WIFI_PASSWORD[] = "";
constexpr char MQTT_HOST[] = "host.wokwi.internal";
constexpr uint16_t MQTT_PORT = 1883;
constexpr char DEVICE_ID[] = "classroom-01";
constexpr char TOPIC_TELEMETRY[] = "smartclassroom/telemetry";
constexpr char TOPIC_STATE[] = "smartclassroom/state";
constexpr char TOPIC_EVENTS[] = "smartclassroom/events";
constexpr char TOPIC_COMMANDS[] = "smartclassroom/commands";
constexpr char TOPIC_AVAILABILITY[] = "smartclassroom/availability";
}

