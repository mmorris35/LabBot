"""Claude API integration for lab result interpretation."""

import json
import logging
from typing import Any

from anthropic import Anthropic, APIError

from labbot.config import settings
from labbot.schemas import InterpretationResponse, LabValue

logger = logging.getLogger(__name__)

# Medical interpretation prompt template
INTERPRETATION_PROMPT_TEMPLATE = (
    """You are a medical lab results interpreter assisting patients with
understanding their results.

For each lab value provided, analyze it and provide:
1. A plain-language explanation of what the test measures
2. Whether the value is normal, borderline, abnormal, or critical based on the reference range
3. What this might indicate for their health (without diagnosing)
4. A citation to an authoritative source (Mayo Clinic, NIH, MedlinePlus, etc.)

Use the reference range (if provided) to determine severity:
- NORMAL: Value within reference range or no reference provided but value seems normal
- BORDERLINE: Slightly outside reference range (1-10% deviation)
- ABNORMAL: Significantly outside reference range (>10% deviation)
- CRITICAL: Values that require immediate medical attention (extreme deviations)

Lab values to interpret:
{lab_values_json}

Respond ONLY with valid JSON matching this exact structure (no markdown, no extra text):
{{
  "results": [
    {{
      "name": "Test Name",
      "value": 14.5,
      "unit": "unit",
      "severity": "normal|borderline|abnormal|critical",
      "explanation": "Plain language explanation",
      "citation": "Source description with URL"
    }}
  ],
  "disclaimer": "Always consult with a healthcare provider for medical advice.",
  "summary": "Optional brief summary of overall results"
}}

Important:
- Return ONLY valid JSON with no additional text or markdown
- Severity must be one of: normal, borderline, abnormal, critical
- Explanation should be 2-3 sentences in plain language
- Citation should include source name and be authoritative
- If you cannot determine severity, mark as 'normal' with explanation of uncertainty
"""
)


def interpret_lab_values(
    lab_values: list[LabValue],
) -> InterpretationResponse:
    """Interpret lab values using Claude Haiku API.

    Uses the Claude Haiku model for cost-efficient interpretation of lab results.
    Handles API errors gracefully by returning 503 error responses.

    Args:
        lab_values: List of LabValue objects to interpret.

    Returns:
        InterpretationResponse containing interpreted results, disclaimer, and summary.

    Raises:
        APIError: If Claude API returns an error (will be caught by caller
                  and converted to 503 response).

    Example:
        >>> lab_value = LabValue(
        ...     name="Hemoglobin",
        ...     value=14.5,
        ...     unit="g/dL",
        ...     reference_min=13.5,
        ...     reference_max=17.5,
        ... )
        >>> response = interpret_lab_values([lab_value])
        >>> isinstance(response, InterpretationResponse)
        True
    """
    # Verify API key is configured
    if not settings.anthropic_api_key:
        logger.error("ANTHROPIC_API_KEY environment variable not set")
        raise ValueError("ANTHROPIC_API_KEY environment variable must be set")

    # Format lab values for the prompt
    lab_values_json: str = json.dumps(
        [
            {
                "name": lab_value.name,
                "value": lab_value.value,
                "unit": lab_value.unit,
                "reference_min": lab_value.reference_min,
                "reference_max": lab_value.reference_max,
            }
            for lab_value in lab_values
        ],
        indent=2,
    )

    # Create prompt with formatted lab values
    prompt: str = INTERPRETATION_PROMPT_TEMPLATE.format(
        lab_values_json=lab_values_json
    )

    logger.info(
        f"Calling Claude Haiku API to interpret {len(lab_values)} lab values"
    )

    try:
        # Initialize Anthropic client
        client: Anthropic = Anthropic(api_key=settings.anthropic_api_key)

        # Call Claude Haiku model
        message: Any = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        # Extract response text
        response_text: str = message.content[0].text

        logger.debug(f"Claude API response: {response_text[:200]}...")

        # Parse JSON response
        try:
            response_data: dict[str, Any] = json.loads(response_text)
        except json.JSONDecodeError as error:
            logger.error(f"Failed to parse Claude API response as JSON: {error}")
            raise ValueError(f"Claude API returned invalid JSON: {response_text}") from error

        # Validate and convert to InterpretationResponse
        interpretation_response: InterpretationResponse = (
            InterpretationResponse(**response_data)
        )

        logger.info("Successfully interpreted lab values")
        return interpretation_response

    except APIError as api_error:
        logger.error(f"Claude API error: {api_error}")
        raise
    except (ValueError, KeyError) as error:
        logger.error(f"Error processing Claude API response: {error}")
        raise
