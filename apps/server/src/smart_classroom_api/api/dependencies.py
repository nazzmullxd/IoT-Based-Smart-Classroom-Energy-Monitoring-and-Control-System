from fastapi import Request

from ..runtime import ApplicationRuntime


def get_runtime(request: Request) -> ApplicationRuntime:
    return request.app.state.runtime
