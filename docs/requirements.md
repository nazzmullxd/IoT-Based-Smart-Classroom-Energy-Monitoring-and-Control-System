# Requirements

## Source-derived requirements

The source methodology requires four layers: sensing/actuation, ESP32 edge control, cloud telemetry/storage, and a dashboard. DHT22 temperature/humidity and occupancy readings feed rules for four relay-controlled loads: AC, fan, lights, and projector. AC/fan use occupancy and environmental conditions; lights use occupancy and operating rules; projector supports manual operation and controlled shutdown. Wi-Fi telemetry must store sensor, state, runtime, energy, and action history. The dashboard must monitor, remotely control, override, and visualize history. Evaluation covers occupied/unoccupied and environmental cases and compares conventional and automated energy using the stated Energy Saving Ratio equation.

## Implementation decisions

- A Wokwi LDR supplies approximate ambient lux, extending the source sensor set to support the source's illuminance variable.
- AUTO thresholds: AC 28/26 °C, fan 25/23.5 °C, lights 150/220 lux (on/off hysteresis).
- Overrides are `AUTO`, `FORCE_ON`, and `FORCE_OFF`. Projector force-off always cools down.
- CONVENTIONAL mode leaves AC, fan, and lights on until explicitly changed; projector remains manual.
- Nominal ratings are AC 1500 W, fan 75 W, lights 120 W, and projector 300 W.
- FastAPI/SQLite emulate the methodology's cloud layer locally. MQTT topics use `smartclassroom/*`.

## Simulation assumptions

Demo timers are occupancy 15 s, AC off 6 s, fan off 3 s, lights off 5 s, and projector cool-down 8 s. Runtime × nominal watts produces **estimated**, not measured, energy. Relay indicators stand in for mains appliances. Wokwi-GUEST is the simulation Wi-Fi; `host.wokwi.internal` reaches host services only through Wokwi's Private IoT Gateway.

## Wokwi limitations

The LDR conversion follows Wokwi's documented RL10/gamma transfer model but is not calibrated. LEDs do not model load current, inrush, power factor, or actual device control protocols. PIR interaction and projector thermal behavior are approximations. No supported, calibrated whole-load power meter is assumed. Local MQTT from the simulator requires Wokwi's Private IoT Gateway (currently a paid feature); the public gateway cannot access the host LAN.

## Future physical-hardware improvements

Use isolated, correctly rated SSR/contactors or manufacturer IR interfaces, a calibrated lux meter, bidirectional people counter, per-load certified power meters, real projector protocol/cool-down timing, TLS/authenticated MQTT, durable local queues, and electrical installation by qualified personnel.
