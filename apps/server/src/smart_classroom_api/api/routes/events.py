from fastapi import APIRouter, Depends, Query

from ..dependencies import get_runtime
from ...runtime import ApplicationRuntime


router = APIRouter(prefix="/api", tags=["analytics"])


@router.get("/energy")
def energy(runtime: ApplicationRuntime = Depends(get_runtime)) -> dict:
    return runtime.database.energy_summary()


@router.get("/events")
def events(
    limit: int = Query(50, ge=1, le=500),
    runtime: ApplicationRuntime = Depends(get_runtime),
) -> list[dict]:
    return runtime.database.events(limit)
