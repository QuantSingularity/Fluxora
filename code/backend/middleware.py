from typing import Awaitable, Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        api_key = request.headers.get("X-API-KEY")
        if not validate_api_key(api_key):
            return JSONResponse(status_code=403, content={"message": "Invalid API key"})
        return await call_next(request)


def validate_api_key(api_key: str | None) -> bool:
    """Validate API key"""
    # TODO: Implement actual API key validation
    return True  # For now, allow all requests
