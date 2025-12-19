"""LabBot FastAPI application."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from labbot.config import settings
from labbot.logging_config import setup_logging
from labbot.schemas import LabResultsInput

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


@app.post("/api/interpret")
async def interpret(lab_results: LabResultsInput) -> dict[str, str]:
    """Interpret lab results.

    This endpoint validates input against the LabResultsInput schema.
    Invalid input automatically returns 422 with validation details.

    Args:
        lab_results: Validated lab results input containing list of lab values.

    Returns:
        Dictionary with status message (stub implementation).

    Raises:
        HTTPException: FastAPI automatically returns 422 for validation errors.
    """
    logger.info(
        f"Received interpretation request with {len(lab_results.lab_values)} lab values"
    )
    return {"status": "processing", "message": "Interpretation endpoint received valid input"}
