from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from routes.prices import router as prices_router
from routes.user_strategy import router as user_strategy_router
from services.auth import get_current_user

app = FastAPI(title="Crypto Analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prices_router)
app.include_router(user_strategy_router)


_STATUS_ERROR_CODES = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    404: "NOT_FOUND",
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
