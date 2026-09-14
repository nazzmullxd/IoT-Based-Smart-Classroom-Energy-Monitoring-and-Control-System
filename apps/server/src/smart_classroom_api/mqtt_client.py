import json
import logging
from collections.abc import Callable

try:
    import paho.mqtt.client as mqtt
except ImportError:  # Allows API/database tests without an MQTT installation.
    mqtt = None


TELEMETRY_TOPIC = "smartclassroom/telemetry"
CONTROL_TOPIC = "smartclassroom/control"
MODE_TOPIC = "smartclassroom/mode"
log = logging.getLogger(__name__)


class MqttService:
    def __init__(
        self,
        on_telemetry: Callable[[dict], bool],
        *,
        host: str = "localhost",
        port: int = 1883,
        enabled: bool = True,
    ) -> None:
        self.on_telemetry = on_telemetry
        self.host = host
        self.port = port
        self.enabled = enabled
        self.connected = False
        self.published: list[tuple[str, dict]] = []
        self.client = None
        if mqtt is not None:
            self.client = mqtt.Client(
                mqtt.CallbackAPIVersion.VERSION2,
                client_id="smart-classroom-backend",
            )
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message

    def start(self) -> None:
        if not self.enabled or self.client is None:
            return
        try:
            self.client.connect_async(self.host, self.port, 30)
            self.client.loop_start()
        except Exception as exc:
            log.warning("MQTT unavailable; API remains usable: %s", exc)

    def stop(self) -> None:
        if self.client is not None:
            self.client.loop_stop()
            if self.connected:
                self.client.disconnect()

    def _on_connect(self, client, userdata, flags, reason_code, properties) -> None:
        self.connected = not bool(reason_code)
        if self.connected:
            client.subscribe(TELEMETRY_TOPIC)

    def _on_disconnect(self, *args) -> None:
        self.connected = False

    def _on_message(self, client, userdata, message) -> None:
        self.handle_message(message.topic, message.payload)

    def handle_message(self, topic: str, payload: bytes | str) -> bool:
        try:
            if isinstance(payload, bytes):
                payload = payload.decode("utf-8")
            data = json.loads(payload)
            if not isinstance(data, dict):
                raise ValueError("payload must be a JSON object")
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            log.warning("Rejected malformed MQTT telemetry: %s", exc)
            return False
        if topic != TELEMETRY_TOPIC:
            return False
        return self.on_telemetry(data)

    def publish_mode(self, mode: str) -> bool:
        return self._publish(MODE_TOPIC, {"mode": mode})

    def publish_control(self, device: str, state: bool) -> bool:
        return self._publish(CONTROL_TOPIC, {"device": device, "state": state})

    def _publish(self, topic: str, payload: dict) -> bool:
        self.published.append((topic, payload))
        if not self.enabled or self.client is None or not self.connected:
            return False
        result = self.client.publish(topic, json.dumps(payload), qos=0)
        return result.rc == mqtt.MQTT_ERR_SUCCESS
