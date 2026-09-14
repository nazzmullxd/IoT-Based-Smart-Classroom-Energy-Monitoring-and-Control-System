#pragma once

#include <Arduino.h>

namespace Config {
// Hardware mapping. Replace only SensorManager when changing LDR to BH1750.
constexpr uint8_t DHT_PIN = 15;
constexpr uint8_t PIR_PIN = 13;
constexpr uint8_t LDR_PIN = 34;
constexpr uint8_t LIGHT_RELAY_PIN = 21;
constexpr uint8_t FAN_RELAY_PIN = 22;
constexpr uint8_t COOLING_RELAY_PIN = 23;
constexpr bool RELAY_ACTIVE_HIGH = true;

// Timing. The physical-prototype value is deliberately easy to select.
constexpr bool SIMULATION_MODE = true;
constexpr unsigned long SENSOR_INTERVAL_MS = 2000;
constexpr unsigned long TELEMETRY_INTERVAL_MS = 3000;
constexpr unsigned long STATUS_INTERVAL_MS = 5000;
constexpr unsigned long WIFI_RETRY_MS = 10000;
constexpr unsigned long MQTT_RETRY_MS = 5000;
constexpr unsigned long OCCUPANCY_TIMEOUT_MS =
    SIMULATION_MODE ? 15000UL : 600000UL;

// Hysteresis: every ON threshold is separated from its OFF threshold.
constexpr float LIGHT_ON_LUX = 150.0f;
constexpr float LIGHT_OFF_LUX = 250.0f;
constexpr float FAN_ON_TEMP_C = 28.0f;
constexpr float FAN_OFF_TEMP_C = 26.0f;
constexpr float COOLING_ON_TEMP_C = 29.0f;
constexpr float COOLING_OFF_TEMP_C = 28.0f;

// Nominal ratings used for estimated energy only; these are not meter readings.
constexpr float LIGHT_POWER_W = 120.0f;
constexpr float FAN_POWER_W = 75.0f;
constexpr float COOLING_POWER_W = 1500.0f;

constexpr char WIFI_SSID[] = "Wokwi-GUEST";
constexpr char WIFI_PASSWORD[] = "";
constexpr char MQTT_HOST[] = "host.wokwi.internal";
constexpr uint16_t MQTT_PORT = 1883;
constexpr char DEVICE_ID[] = "classroom-01";

constexpr char TOPIC_TELEMETRY[] = "smartclassroom/telemetry";
constexpr char TOPIC_CONTROL[] = "smartclassroom/control";
constexpr char TOPIC_MODE[] = "smartclassroom/mode";

static_assert(LIGHT_ON_LUX < LIGHT_OFF_LUX, "Light hysteresis is invalid");
static_assert(FAN_OFF_TEMP_C < FAN_ON_TEMP_C, "Fan hysteresis is invalid");
static_assert(
    COOLING_OFF_TEMP_C < COOLING_ON_TEMP_C,
    "Cooling hysteresis is invalid");
static_assert(
    FAN_ON_TEMP_C < COOLING_ON_TEMP_C,
    "Cooling threshold must exceed fan threshold");
}
