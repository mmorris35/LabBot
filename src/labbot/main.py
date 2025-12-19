"""LabBot FastAPI application."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from labbot.config import settings
from labbot.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

MEDICAL_DISCLAIMER = """
DISCLAIMER: LabBot provides educational information only and is not a substitute
for professional medical advice, diagnosis, or treatment. Always consult with a
qualified healthcare provider about your lab results.
"""

app = FastAPI(
    title=settings.app_title,
    description=f"{settings.app_description}\n\n{MEDICAL_DISCLAIMER}",
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

logger.info("LabBot application initialized with CORS enabled")


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint with API info."""
    return {"message": "LabBot API", "version": settings.app_version}


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        Dictionary with status field set to "healthy".
    """
    return {"status": "healthy"}
