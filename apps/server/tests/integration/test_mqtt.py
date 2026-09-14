from smart_classroom_api.mqtt_client import MqttService, TELEMETRY_TOPIC


def test_malformed_mqtt_telemetry_is_rejected():
    service = MqttService(lambda payload: True, enabled=False)
    assert service.handle_message(TELEMETRY_TOPIC, b"not-json") is False


def test_valid_mqtt_telemetry_reaches_handler():
    received = []
    service = MqttService(lambda payload: received.append(payload) or True, enabled=False)
    assert service.handle_message(TELEMETRY_TOPIC, '{"occupancy": true}') is True
    assert received == [{"occupancy": True}]
