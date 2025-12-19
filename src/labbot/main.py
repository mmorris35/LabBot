"""LabBot FastAPI application."""

import logging
from pathlib import Path
from typing import Any

from anthropic import APIError
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from labbot.config import settings
from labbot.interpreter import interpret_lab_values
from labbot.logging_config import setup_logging
from labbot.pii_detector import detect_pii_in_dict
from labbot.schemas import InterpretationResponse, LabResultsInput

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

# Mount static files (HTML, CSS, JS)
static_dir: Path = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    logger.info(f"Static files mounted from {static_dir}")
else:
    logger.warning(f"Static directory not found at {static_dir}")

logger.info("LabBot application initialized with CORS enabled")


@app.get("/", response_model=None)
async def root() -> FileResponse | HTMLResponse:
    """Root endpoint serving the main UI page.

    Returns:
        FileResponse | HTMLResponse: The index.html file or fallback HTML.
    """
    index_file: Path = Path(__file__).parent / "static" / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    # Fallback if static file not found
    return HTMLResponse(
        "<html><body><h1>LabBot</h1><p>Static files not found</p></body></html>"
    )


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        Dictionary with status field set to "healthy".
    """
    return {"status": "healthy"}


@app.post("/api/interpret")
async def interpret(lab_results: LabResultsInput) -> InterpretationResponse:
    """Interpret lab results.

    This endpoint validates input against the LabResultsInput schema and checks
    for personally identifiable information (PII). If PII is detected, returns
    a 400 error without processing the request. Clean data is sent to Claude API
    for interpretation.

    Pipeline:
    1. Schema validation (automatic via Pydantic)
    2. PII detection gate (returns 400 if detected)
    3. Claude API interpretation (returns results or 503 on error)

    Args:
        lab_results: Validated lab results input containing list of lab values.

    Returns:
        InterpretationResponse with interpreted results, disclaimer, and summary.

    Raises:
        HTTPException: 400 if PII is detected in the input.
        HTTPException: 503 if Claude API returns an error.
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

    # Call Claude API for interpretation
    try:
        interpretation_response: InterpretationResponse = interpret_lab_values(
            lab_results.lab_values
        )
        logger.info(
            f"Successfully interpreted {len(lab_results.lab_values)} lab values "
            f"[{request_log_id}]"
        )
        return interpretation_response

    except APIError as api_error:
        logger.error(
            f"Claude API error while interpreting lab values [{request_log_id}]: {api_error}"
        )
        raise HTTPException(
            status_code=503,
            detail="Failed to interpret lab results due to API error. Please try again later.",
        ) from api_error
    except (ValueError, KeyError) as error:
        logger.error(
            f"Error processing Claude API response [{request_log_id}]: {error}"
        )
        raise HTTPException(
            status_code=503,
            detail="Failed to process lab interpretation. Please try again later.",
        ) from error
