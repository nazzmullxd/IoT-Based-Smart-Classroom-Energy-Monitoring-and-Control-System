from fastapi import APIRouter, Depends

from ..dependencies import get_runtime
from ...runtime import ApplicationRuntime


router = APIRouter(prefix="/api", tags=["health"])


@router.get("/status")
def status(runtime: ApplicationRuntime = Depends(get_runtime)) -> dict:
    return {
        "service": "ok",
        "mqttConnected": runtime.mqtt.connected,
        "latest": runtime.database.latest(),
    }
