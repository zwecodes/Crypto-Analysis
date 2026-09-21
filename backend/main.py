import os

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from routes.backtest import router as backtest_router
from routes.indicators import router as indicators_router
from routes.prices import router as prices_router
from routes.signals import router as signals_router
from routes.user_strategy import router as user_strategy_router
from services.auth import get_current_user
from services.rate_limit import RateLimitMiddleware

app = FastAPI(title="Crypto Analysis API")

# CORS: set CORS_ORIGINS="https://app.example.com,http://localhost:5173"
# to tighten. Default remains open for local + Vercel while the frontend URL is fluid.
_cors_raw = os.getenv("CORS_ORIGINS", "*").strip()
_cors_origins = (
    ["*"]
    if _cors_raw == "*"
    else [origin.strip() for origin in _cors_raw.split(",") if origin.strip()]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.add_middleware(RateLimitMiddleware, limit=60, window_seconds=60.0)

app.include_router(prices_router)
app.include_router(indicators_router)
app.include_router(signals_router)
app.include_router(backtest_router)
app.include_router(user_strategy_router)


_STATUS_ERROR_CODES = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    404: "NOT_FOUND",
    429: "RATE_LIMITED",
    500: "INTERNAL_ERROR",
}


def _contract_error(detail, status_code: int) -> dict:
    if isinstance(detail, dict) and "code" in detail and "message" in detail:
        return {"code": str(detail["code"]), "message": str(detail["message"])}
    message = detail if isinstance(detail, str) and detail else str(detail or "An error occurred")
    return {
        "code": _STATUS_ERROR_CODES.get(status_code, "ERROR"),
        "message": message,
    }


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": _contract_error(exc.detail, exc.status_code)},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    message = "; ".join(
        f"{'.'.join(str(loc) for loc in err.get('loc', []))}: {err.get('msg')}"
        for err in exc.errors()
    )
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": "BAD_REQUEST",
                "message": message or "Invalid request",
            }
        },
    )


@app.get("/")
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/example")
def example(user_id: str = Depends(get_current_user)):
    return {"user_id": user_id}
