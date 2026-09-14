from contextlib import asynccontextmanager

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import Settings
from .database import Database
from .models import ControlRequest, ModeRequest, Telemetry
from .mqtt_client import MqttService


def create_app(
    settings: Settings | None = None,
    *,
    database: Database | None = None,
    mqtt_service: MqttService | None = None,
) -> FastAPI:
    settings = settings or Settings.from_env()
    database = database or Database(settings.database_path, settings.powers)

    def accept_telemetry(raw: dict) -> bool:
        try:
            telemetry = Telemetry.model_validate(raw)
        except Exception:
            return False
        return database.save(telemetry.model_dump(mode="json"))

    mqtt_service = mqtt_service or MqttService(
        accept_telemetry,
        host=settings.mqtt_host,
        port=settings.mqtt_port,
        enabled=settings.mqtt_enabled,
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        mqtt_service.start()
        yield
        mqtt_service.stop()

    app = FastAPI(
        title="Smart Classroom Research Prototype",
        version="2.0.0",
        lifespan=lifespan,
    )
    app.state.database = database
    app.state.mqtt = mqtt_service
    app.state.accept_telemetry = accept_telemetry

    @app.get("/", include_in_schema=False)
    def dashboard() -> FileResponse:
        return FileResponse(settings.dashboard_path / "index.html")

    @app.get("/api/status")
    def status() -> dict:
        latest = database.latest()
        return {
            "available": latest is not None,
            "mqtt_connected": mqtt_service.connected,
            "latest": latest,
            "configuration": {
                "light_on_lux": settings.light_on_lux,
                "light_off_lux": settings.light_off_lux,
                "fan_on_temp_c": settings.fan_on_temp_c,
                "fan_off_temp_c": settings.fan_off_temp_c,
                "cooling_on_temp_c": settings.cooling_on_temp_c,
                "cooling_off_temp_c": settings.cooling_off_temp_c,
                "occupancy_timeout_seconds": settings.occupancy_timeout_seconds,
            },
        }

    @app.get("/api/history")
    def history(limit: int = Query(100, ge=1, le=1000)) -> list[dict]:
        return database.history(limit)

    @app.get("/api/energy")
    def energy() -> dict:
        return database.energy_summary()

    @app.post("/api/mode")
    def set_mode(request: ModeRequest) -> dict:
        accepted = mqtt_service.publish_mode(request.mode)
        return {"accepted": accepted, "mode": request.mode}

    @app.post("/api/control")
    def control(request: ControlRequest) -> dict:
        accepted = mqtt_service.publish_control(request.device, request.state)
        return {
            "accepted": accepted,
            "device": request.device,
            "state": request.state,
            "note": "Direct commands are applied by the ESP32 only in MANUAL mode.",
        }

    @app.post("/api/telemetry", include_in_schema=False)
    def inject_for_tests(payload: Telemetry) -> dict:
        return {"stored": accept_telemetry(payload.model_dump(mode="json"))}

    app.mount("/static", StaticFiles(directory=settings.dashboard_path), name="static")
    return app


app = create_app()
