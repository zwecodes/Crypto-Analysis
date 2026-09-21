"""Simple per-IP rate limiter middleware for FastAPI/Starlette."""

from __future__ import annotations

import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Allow `limit` requests per `window_seconds` per client IP."""

    def __init__(
        self,
        app,
        limit: int = 60,
        window_seconds: float = 60.0,
        exempt_paths: frozenset[str] | None = None,
    ) -> None:
        super().__init__(app)
        self.limit = limit
        self.window_seconds = window_seconds
        self.exempt_paths = exempt_paths or frozenset({"/", "/health"})
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def _client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "unknown"

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in self.exempt_paths:
            return await call_next(request)

        ip = self._client_ip(request)
        now = time.monotonic()
        window = self._hits[ip]

        while window and window[0] <= now - self.window_seconds:
            window.popleft()

        if len(window) >= self.limit:
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMITED",
                        "message": (
                            f"Too many requests. Limit is {self.limit} "
                            f"per {int(self.window_seconds)} seconds."
                        ),
                    }
                },
                headers={"Retry-After": str(int(self.window_seconds))},
            )

        window.append(now)
        return await call_next(request)
