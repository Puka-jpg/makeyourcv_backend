import os
from contextlib import asynccontextmanager
from typing import Awaitable, Callable
from uuid import uuid4

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from adk.routes import router as adk_routes
from db import sessionmanager
from routes.auth_routes.auth import router as auth_routes
from schemas.common import ErrorResponseSchema
from settings import settings
from utils.constants import API_RATE_LIMIT
from utils.logger import RequestContextVar, get_logger, request_ctx_var

logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize db pool
    if not sessionmanager.session_factory:
        sessionmanager.init_db()

    yield
    await sessionmanager.close()


app = FastAPI(
    title="Resume-Builder",
    lifespan=lifespan,
    responses={
        status.HTTP_429_TOO_MANY_REQUESTS: {
            "model": ErrorResponseSchema,
            "description": "Rate Limit Response",
        }
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


limiter = Limiter(
    key_func=get_remote_address,
)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceed_handler(request: Request, exc: RateLimitExceeded):
    response = JSONResponse(
        {"detail": "Rate limit exceeded"},
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    )
    response = request.app.state.limiter._inject_headers(
        response, getattr(request.state, "view_rate_limit", None)
    )
    return response


@app.middleware("http")
async def logging_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    request_id = str(uuid4())
    request_path = f"{request.method} {request.url.path}"
    request_ctx_var.set(
        RequestContextVar(request_id=request_id, request_path=request_path)
    )
    extra = {}
    if settings.ENV == "local":
        extra["query"] = str(request.query_params)
    logger.info(
        "Incoming Request",
        extra={"method": request.method, "path": request.url.path, "extra": extra},
    )
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


app.include_router(auth_routes, prefix="/api/auth", tags=["Auth"])

app.include_router(adk_routes, prefix="/api/v1")

os.makedirs("generated_resumes", exist_ok=True)
app.mount(
    "/generated_resumes",
    StaticFiles(directory="generated_resumes"),
    name="generated_resumes",
)


@app.get("/", tags=["Health"])
@limiter.limit(API_RATE_LIMIT)
async def healthz(request: Request) -> str:
    return "ok!"
