import json
import logging
from collections.abc import Callable

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None


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
        self.connected = False
        self.client = None
        self.host = host
        self.port = port
        self.enabled = enabled

        if mqtt is not None:
            self.client = mqtt.Client(
                mqtt.CallbackAPIVersion.VERSION2,
                client_id="smartclassroom-backend",
            )
            self.client.on_connect = self._connect
            self.client.on_disconnect = self._disconnect
            self.client.on_message = self._message

    def start(self) -> None:
        if not self.enabled or self.client is None:
            return
        try:
            self.client.connect_async(self.host, self.port, 30)
            self.client.loop_start()
        except Exception as exc:
            log.warning("MQTT startup deferred: %s", exc)

    def stop(self) -> None:
        if self.client is not None:
            self.client.loop_stop()
            self.client.disconnect()

    def _connect(self, client, userdata, flags, reason_code, properties) -> None:
        self.connected = not bool(reason_code)
        if self.connected:
            client.subscribe("smartclassroom/telemetry")
            log.info("MQTT connected")

    def _disconnect(self, *args) -> None:
        self.connected = False

    def _message(self, client, userdata, message) -> None:
        try:
            self.on_telemetry(json.loads(message.payload.decode("utf-8")))
        except Exception:
            log.exception("Rejected telemetry")

    def publish(self, payload: dict) -> bool:
        if not self.enabled or self.client is None:
            return False
        result = self.client.publish(
            "smartclassroom/commands",
            json.dumps(payload),
            qos=0,
        )
        return result.rc == mqtt.MQTT_ERR_SUCCESS
