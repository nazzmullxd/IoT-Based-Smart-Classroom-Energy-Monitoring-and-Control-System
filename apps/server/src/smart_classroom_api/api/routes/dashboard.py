from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from ..dependencies import get_runtime
from ...runtime import ApplicationRuntime


router = APIRouter(include_in_schema=False)


@router.get("/")
def dashboard(runtime: ApplicationRuntime = Depends(get_runtime)) -> FileResponse:
    return FileResponse(runtime.settings.dashboard_path / "index.html")
