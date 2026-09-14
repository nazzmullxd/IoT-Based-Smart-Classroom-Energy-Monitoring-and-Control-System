from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .api.routes import commands, dashboard, events, health, telemetry
from .config import Settings
from .runtime import ApplicationRuntime


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    runtime = ApplicationRuntime(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await runtime.start()
        try:
            yield
        finally:
            runtime.stop()

    app = FastAPI(
        title="Smart Classroom API",
        version="1.0.0",
        lifespan=lifespan,
    )
    app.state.runtime = runtime
    app.include_router(dashboard.router)
    app.include_router(health.router)
    app.include_router(telemetry.router)
    app.include_router(events.router)
    app.include_router(commands.router)
    app.mount(
        "/static",
        StaticFiles(directory=settings.dashboard_path),
        name="static",
    )
    return app


app = create_app()
