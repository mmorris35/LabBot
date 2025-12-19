"""LabBot FastAPI application."""

import logging
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from labbot.config import settings
from labbot.logging_config import setup_logging
from labbot.pii_detector import detect_pii_in_dict
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

    This endpoint validates input against the LabResultsInput schema and checks
    for personally identifiable information (PII). If PII is detected, returns
    a 400 error without processing the request.

    Args:
        lab_results: Validated lab results input containing list of lab values.

    Returns:
        Dictionary with status message (stub implementation for non-PII data).

    Raises:
        HTTPException: 400 if PII is detected in the input.
        HTTPException: FastAPI automatically returns 422 for validation errors.
    """
    request_log_id: str = f"interpret-{id(lab_results)}"

    # Convert LabResultsInput to dict for PII detection
    lab_results_dict: dict[str, Any] = lab_results.model_dump()

    # Check for PII in the request
    detected_pii: list[str] = detect_pii_in_dict(lab_results_dict)

    if detected_pii:
        # Log PII detection without including the actual PII data
        logger.warning(
            f"PII detected in request [{request_log_id}]: types={detected_pii}. "
            "Request rejected."
        )
        raise HTTPException(
            status_code=400,
            detail={
                "error": "PII detected",
                "types": detected_pii,
            },
        )

    logger.info(
        f"Received interpretation request [{request_log_id}] with "
        f"{len(lab_results.lab_values)} lab values (PII check passed)"
    )
    return {"status": "processing", "message": "Interpretation endpoint received valid input"}
