import asyncio
import logging

from .config import Settings
from .domain.models import Telemetry
from .infrastructure.database import Database
from .infrastructure.mqtt import MqttService


class EventHub:
    def __init__(self) -> None:
        self._subscribers: set[asyncio.Queue] = set()

    def subscribe(self) -> asyncio.Queue:
        queue = asyncio.Queue(maxsize=20)
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        self._subscribers.discard(queue)

    def publish(self, item: dict) -> None:
        for queue in list(self._subscribers):
            if queue.full():
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    pass
            queue.put_nowait(item)


class ApplicationRuntime:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.database = Database(str(settings.database_path))
        self.events = EventHub()
        self.loop: asyncio.AbstractEventLoop | None = None
        self.mqtt = MqttService(
            self.accept_telemetry,
            host=settings.mqtt_host,
            port=settings.mqtt_port,
            enabled=settings.mqtt_enabled,
        )

    async def start(self) -> None:
        self.loop = asyncio.get_running_loop()
        self.mqtt.start()

    def stop(self) -> None:
        self.mqtt.stop()

    def accept_telemetry(self, raw: dict) -> bool:
        try:
            data = Telemetry.model_validate(raw).model_dump()
        except Exception as exc:
            logging.warning("Invalid telemetry: %s", exc)
            return False

        self.database.save_telemetry(data)
        if self.loop is not None:
            self.loop.call_soon_threadsafe(self.events.publish, data)
        return True
