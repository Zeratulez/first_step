import time
import uuid
import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())[:8]

        start_time = time.perf_counter()

        log = logger.bind(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )
        log.info("request_started")

        try:
            response = await call_next(request)
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

            log_method = log.warning if duration_ms > 1000 else log.info
            log_method(
                "request_finished",
                status_code=response.status_code,
                duration_ms=duration_ms
            )
            return response
        except Exception as e:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            log.error(
                "request_failed",
                duration_ms=duration_ms,
                exc_info=True
            )
            raise