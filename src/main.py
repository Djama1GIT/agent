from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from src.api import main_api_router
from src.core.config import Settings
from src.core.errors.handlers import exception_handlers
from src.core.logger import configure_logging

# Load application configuration
settings = Settings()  # type: ignore[call-arg]

# Configure application logging
configure_logging(settings=settings)

# Initialize main FastAPI application with metadata from settings
app = FastAPI(
    title=settings.TITLE,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    summary=settings.SUMMARY,
    contact=settings.CONTACT,
    license_info=settings.LICENSE_INFO,
    exception_handlers=exception_handlers,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=settings.ALLOW_CREDENTIALS,
    allow_methods=settings.ALLOW_METHODS,
    allow_headers=settings.ALLOW_HEADERS,
)

# Include API routes
app.include_router(main_api_router, prefix="/api")

# Instrument the application with Prometheus metrics
Instrumentator(
    should_instrument_requests_inprogress=True,
    inprogress_labels=True,
).instrument(app).expose(app)
