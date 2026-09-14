from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import get_runtime
from ...domain.models import ControlRequest, ModeRequest, ResetRequest
from ...runtime import ApplicationRuntime


router = APIRouter(prefix="/api", tags=["commands"])
DEVICE_NAMES = {"ac", "fan", "lights", "projector"}


@router.post("/control/{device}")
def control(
    device: str,
    request: ControlRequest,
    runtime: ApplicationRuntime = Depends(get_runtime),
) -> dict:
    if device not in DEVICE_NAMES:
        raise HTTPException(404, "Unknown device")

    accepted = runtime.mqtt.publish(
        {"command": "override", "device": device, "value": request.value}
    )
    result = "published" if accepted else "broker unavailable"
    runtime.database.log_action("dashboard", device, request.value, result)
    return {"accepted": accepted, "result": result}


@router.post("/mode")
def mode(
    request: ModeRequest,
    runtime: ApplicationRuntime = Depends(get_runtime),
) -> dict:
    accepted = runtime.mqtt.publish({"command": "mode", "value": request.mode})
    runtime.database.log_action(
        "dashboard",
        None,
        f"MODE {request.mode}",
        "published" if accepted else "broker unavailable",
    )
    return {"accepted": accepted}


@router.post("/reset")
def reset(
    request: ResetRequest,
    runtime: ApplicationRuntime = Depends(get_runtime),
) -> dict:
    accepted = runtime.mqtt.publish({"command": "reset", "value": request.target})
    runtime.database.log_action(
        "dashboard",
        None,
        f"RESET {request.target}",
        "published" if accepted else "broker unavailable",
    )
    return {"accepted": accepted}
