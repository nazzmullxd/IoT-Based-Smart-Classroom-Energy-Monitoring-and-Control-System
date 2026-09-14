#pragma once

#include <PubSubClient.h>
#include <WiFi.h>

typedef void (*CommandHandler)(const char *payload);

class NetworkManager {
 public:
  NetworkManager();
  void begin(CommandHandler handler);
  void loop(unsigned long now);
  bool publish(const char *topic, const char *payload, bool retained = false);
  bool wifiConnected() const { return WiFi.status() == WL_CONNECTED; }
  bool mqttConnected() { return mqtt_.connected(); }

 private:
  WiFiClient wifiClient_;
  PubSubClient mqtt_;
  unsigned long lastWifiAttempt_ = 0;
  unsigned long lastMqttAttempt_ = 0;
  static CommandHandler handler_;
  static void callback(char *topic, byte *payload, unsigned int length);
};
