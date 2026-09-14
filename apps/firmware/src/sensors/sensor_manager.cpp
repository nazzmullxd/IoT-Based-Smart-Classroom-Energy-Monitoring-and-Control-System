#include "smart_classroom/sensors/sensor_manager.h"

#include <math.h>

#include "smart_classroom/config.h"

SensorManager::SensorManager() : dht_(Config::DHT_PIN, DHT22) {}

void SensorManager::begin() { dht_.begin(); analogReadResolution(12); }

float SensorManager::rawToLux(int raw, bool &error) {
  error = false;
  if (raw <= 0) {
    return 100000.0f;
  }
  if (raw >= 4095) {
    error = true;
    return 0.0f;
  }

  constexpr float GAMMA = 0.7f;
  constexpr float RL10_KOHM = 50.0f;
  const float voltage = raw / 4095.0f * 3.3f;
  const float resistance = 10000.0f * voltage / (3.3f - voltage);
  const float lux = powf(RL10_KOHM * 1000.0f * powf(10.0f, GAMMA) /
                             max(resistance, 1.0f),
                         1.0f / GAMMA);
  if (!isfinite(lux)) {
    error = true;
    return 0.0f;
  }
  return constrain(lux, 0.0f, 100000.0f);
}

bool SensorManager::update(unsigned long now, bool occupied) {
  if (lastReadMs_ && (unsigned long)(now - lastReadMs_) < Config::SENSOR_INTERVAL_MS) {
    reading_.occupied = occupied;
    reading_.pirRaw = digitalRead(Config::PIR_PIN);
    return false;
  }

  lastReadMs_ = now;
  reading_.uptimeMs = now;
  reading_.occupied = occupied;
  reading_.pirRaw = digitalRead(Config::PIR_PIN);

  float h = dht_.readHumidity();
  float t = dht_.readTemperature();
  const bool dhtError = isnan(h) || isnan(t);
  if (!dhtError) {
    reading_.humidityPct = h;
    reading_.temperatureC = t;
  }

  reading_.ldrRaw = analogRead(Config::LDR_PIN);
  bool ldrError = false;
  reading_.illuminanceLux = rawToLux(reading_.ldrRaw, ldrError);
  reading_.sensorError = dhtError || ldrError;
  return true;
}
