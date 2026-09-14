import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from ..dependencies import get_runtime
from ...domain.models import Telemetry
from ...runtime import ApplicationRuntime


router = APIRouter(prefix="/api", tags=["telemetry"])


@router.get("/telemetry/latest")
def latest(runtime: ApplicationRuntime = Depends(get_runtime)) -> dict:
    value = runtime.database.latest()
    if value is None:
        raise HTTPException(404, "No telemetry received")
    return value


@router.get("/telemetry/history")
def history(
    limit: int = Query(100, ge=1, le=1000),
    runtime: ApplicationRuntime = Depends(get_runtime),
) -> list[dict]:
    return runtime.database.history(limit)


@router.get("/devices")
def devices(runtime: ApplicationRuntime = Depends(get_runtime)) -> dict:
    return (runtime.database.latest() or {}).get("devices", {})


@router.post("/telemetry", include_in_schema=False)
def inject_for_testing(
    payload: Telemetry,
    runtime: ApplicationRuntime = Depends(get_runtime),
) -> dict:
    runtime.accept_telemetry(payload.model_dump())
    return {"stored": True}


@router.get("/stream")
async def stream(
    runtime: ApplicationRuntime = Depends(get_runtime),
) -> StreamingResponse:
    queue = runtime.events.subscribe()

    async def generate():
        try:
            while True:
                try:
                    item = await asyncio.wait_for(queue.get(), 15)
                    yield f"data: {json.dumps(item)}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            runtime.events.unsubscribe(queue)

    return StreamingResponse(generate(), media_type="text/event-stream")
