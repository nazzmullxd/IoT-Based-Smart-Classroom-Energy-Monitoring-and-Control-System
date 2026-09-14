#include "smart_classroom/connectivity/network_manager.h"

#include "smart_classroom/config.h"

CommandHandler NetworkManager::handler_ = nullptr;

NetworkManager::NetworkManager() : mqtt_(wifiClient_) {}

void NetworkManager::begin(CommandHandler handler) {
  handler_ = handler;
  WiFi.mode(WIFI_STA);
  WiFi.begin(Config::WIFI_SSID, Config::WIFI_PASSWORD);
  mqtt_.setServer(Config::MQTT_HOST, Config::MQTT_PORT);
  mqtt_.setCallback(callback);
  mqtt_.setBufferSize(2048);
}

void NetworkManager::callback(char *, byte *payload, unsigned int length) {
  if (!handler_ || length >= 1024) {
    return;
  }
  char message[1024];
  memcpy(message, payload, length);
  message[length] = '\0';
  handler_(message);
}

void NetworkManager::loop(unsigned long now) {
  if (WiFi.status() != WL_CONNECTED) {
    if ((unsigned long)(now - lastWifiAttempt_) >= Config::WIFI_RETRY_MS) {
      lastWifiAttempt_ = now;
      WiFi.disconnect();
      WiFi.begin(Config::WIFI_SSID, Config::WIFI_PASSWORD);
      Serial.println("[EVENT] WiFi reconnect");
    }
    return;
  }

  if (!mqtt_.connected()) {
    if ((unsigned long)(now - lastMqttAttempt_) >= Config::MQTT_RETRY_MS) {
      lastMqttAttempt_ = now;
      String clientId = String(Config::DEVICE_ID) + "-" +
                        String((uint32_t)ESP.getEfuseMac(), HEX);
      if (mqtt_.connect(
              clientId.c_str(),
              Config::TOPIC_AVAILABILITY,
              0,
              true,
              "offline")) {
        mqtt_.subscribe(Config::TOPIC_COMMANDS);
        mqtt_.publish(Config::TOPIC_AVAILABILITY, "online", true);
        Serial.println("[EVENT] MQTT connected");
      }
    }
    return;
  }

  mqtt_.loop();
}

bool NetworkManager::publish(const char *topic, const char *payload, bool retained) {
  return mqtt_.connected() && mqtt_.publish(topic, payload, retained);
}
