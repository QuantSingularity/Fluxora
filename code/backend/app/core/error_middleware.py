import logging
import traceback
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

logger = logging.getLogger(__name__)


class ErrorDetail:
    def __init__(
        self,
        code: str,
        message: str,
        detail: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.code = code
        self.message = message
        self.detail = detail
        self.context = context or {}

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {"code": self.code, "message": self.message}
        if self.detail:
            result["detail"] = self.detail
        if self.context:
            result["context"] = self.context
        return result


class ErrorResponse:
    def __init__(
        self,
        error: ErrorDetail,
        request_id: Optional[str] = None,
        status_code: int = 500,
    ) -> None:
        self.error = error
        self.request_id = request_id
        self.status_code = status_code

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {"error": self.error.to_dict()}
        if self.request_id:
            result["request_id"] = self.request_id
        return result


def add_error_handlers(app: FastAPI) -> None:
    """Add error handlers to the FastAPI application."""

    def _make_serializable(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: _make_serializable(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_make_serializable(i) for i in obj]
        if isinstance(obj, Exception):
            return str(obj)
        return obj

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        serializable_errors = _make_serializable(exc.errors())
        error_detail = ErrorDetail(
            code="VALIDATION_ERROR",
            message="Request validation failed",
            detail=str(exc),
            context={"errors": serializable_errors},
        )
        error_response = ErrorResponse(
            error=error_detail,
            request_id=request.headers.get("X-Request-ID"),
            status_code=422,
        )
        return JSONResponse(status_code=422, content=error_response.to_dict())

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        error_detail = ErrorDetail(
            code=f"HTTP_{exc.status_code}",
            message=str(exc.detail),
            context={"headers": dict(exc.headers)} if exc.headers else {},
        )
        error_response = ErrorResponse(
            error=error_detail,
            request_id=request.headers.get("X-Request-ID"),
            status_code=exc.status_code,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.to_dict(),
            headers=dict(exc.headers) if exc.headers else None,
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception("Unhandled exception during request %s", request.url)
        error_detail = ErrorDetail(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred",
            detail=str(exc),
            context={"traceback": traceback.format_exc()},
        )
        error_response = ErrorResponse(
            error=error_detail,
            request_id=request.headers.get("X-Request-ID"),
            status_code=500,
        )
        return JSONResponse(status_code=500, content=error_response.to_dict())
