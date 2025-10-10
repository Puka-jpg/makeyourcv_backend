from typing import Awaitable, Callable
from uuid import uuid4

from fastapi import FastAPI, Request, Response

from settings import settings
from utils.logger import RequestContextVar, get_logger, request_ctx_var

logger = get_logger()

app = FastAPI(title="Resume-Builder")


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
        extra["query"] = request.query_params  # type: ignore
    logger.info("REquest log", extra=extra)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/", tags=["Health"])
async def healthz():
    return "ok!"
