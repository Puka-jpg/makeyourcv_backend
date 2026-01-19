from contextlib import asynccontextmanager
from typing import Awaitable, Callable
from uuid import uuid4

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from db import sessionmanager
from routes.auth_routes.auth import router as auth_routes
from routes.cv_parser_routes.cv_parser import router as cv_parser_routes
from routes.user_input_routes.certification_routes import router as certification_routes
from routes.user_input_routes.custom_section_routes import (
    router as custom_section_routes,
)
from routes.user_input_routes.education_routes import router as education_routes
from routes.user_input_routes.experience_routes import router as experience_routes
from routes.user_input_routes.personal_info_routes import router as personal_info_routes
from routes.user_input_routes.project_routes import router as project_routes
from routes.user_input_routes.publication_routes import router as publication_routes
from routes.user_input_routes.summary_routes import router as summary_routes
from routes.user_input_routes.technical_skill_routes import (
    router as technical_skill_routes,
)
from routes.user_input_routes.user_routes import router as user_routes
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
        extra["query"] = request.query_params  # type: ignore
    logger.info("REquest log", extra=extra)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


app.include_router(cv_parser_routes, prefix="/api/cv_parser", tags=["CV parser"])
app.include_router(auth_routes, prefix="/api/auth", tags=["Auth"])
app.include_router(user_routes, prefix="/api/users", tags=["User Management"])
app.include_router(
    personal_info_routes, prefix="/api/personal-info", tags=["Personal Info"]
)
app.include_router(summary_routes, prefix="/api/summary", tags=["Summary"])
app.include_router(education_routes, prefix="/api/education", tags=["Education"])
app.include_router(experience_routes, prefix="/api/experiences", tags=["Experience"])
app.include_router(project_routes, prefix="/api/projects", tags=["Projects"])
app.include_router(
    technical_skill_routes, prefix="/api/technical-skills", tags=["Technical Skills"]
)
app.include_router(
    publication_routes, prefix="/api/publications", tags=["Publications"]
)
app.include_router(
    certification_routes, prefix="/api/certifications", tags=["Certifications"]
)
app.include_router(
    custom_section_routes, prefix="/api/custom-sections", tags=["Custom Sections"]
)


@app.get("/", tags=["Health"])
@limiter.limit(API_RATE_LIMIT)
async def healthz(request: Request) -> str:
    return "ok!"
