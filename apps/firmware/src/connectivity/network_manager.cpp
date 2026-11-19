#include "smart_classroom/connectivity/network_manager.h"

#include "smart_classroom/config.h"

CommandHandler ClassroomNetwork::handler_ = nullptr;

ClassroomNetwork::ClassroomNetwork() : mqtt_(wifiClient_) {}

void ClassroomNetwork::begin(CommandHandler handler) {
  handler_ = handler;
  WiFi.mode(WIFI_STA);
  WiFi.begin(Config::WIFI_SSID, Config::WIFI_PASSWORD);
  mqtt_.setServer(Config::MQTT_HOST, Config::MQTT_PORT);
  mqtt_.setCallback(callback);
  mqtt_.setBufferSize(1024);
}

void ClassroomNetwork::callback(char *topic, byte *payload, unsigned int length) {
  if (!handler_ || length >= 512) return;
  char message[512];
  memcpy(message, payload, length);
  message[length] = '\0';
  handler_(topic, message);
}

void ClassroomNetwork::loop(unsigned long now) {
  if (WiFi.status() != WL_CONNECTED) {
    if ((unsigned long)(now - lastWifiAttempt_) >= Config::WIFI_RETRY_MS) {
      lastWifiAttempt_ = now;
      WiFi.disconnect();
      WiFi.begin(Config::WIFI_SSID, Config::WIFI_PASSWORD);
    }
    return;  // Sensor acquisition and control continue in the main loop.
  }

  if (!mqtt_.connected()) {
    if ((unsigned long)(now - lastMqttAttempt_) >= Config::MQTT_RETRY_MS) {
      lastMqttAttempt_ = now;
      const String clientId = String(Config::DEVICE_ID) + "-" +
                              String((uint32_t)ESP.getEfuseMac(), HEX);
      if (mqtt_.connect(clientId.c_str())) {
        mqtt_.subscribe(Config::TOPIC_CONTROL);
        mqtt_.subscribe(Config::TOPIC_MODE);
        Serial.println("[NETWORK] MQTT connected");
      }
    }
    return;
  }
  mqtt_.loop();
}

bool ClassroomNetwork::publish(const char *topic, const char *payload, bool retained) {
  return mqtt_.connected() && mqtt_.publish(topic, payload, retained);
}
