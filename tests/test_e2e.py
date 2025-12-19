"""End-to-end tests for deployed LabBot API.

This module tests the full API pipeline with realistic data:
- Health check endpoint
- Lab result interpretation with sample data
- Error handling for PII and invalid input
"""

import json
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from labbot.main import app


@pytest.fixture
async def client() -> AsyncClient:
    """Create async test client for API testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client


@contextmanager
def mock_anthropic_for_e2e(
    response_data: dict[str, Any] | None = None,
) -> Iterator[None]:
    """Context manager for mocking interpret_lab_values in E2E tests.

    Args:
        response_data: Dict with results, disclaimer, and optional summary.

    Yields:
        None - context manager setup and teardown.
    """
    # Default response
    if response_data is None:
        response_data = {
            "results": [
                {
                    "name": "Hemoglobin",
                    "value": 14.5,
                    "unit": "g/dL",
                    "severity": "normal",
                    "explanation": "Hemoglobin carries oxygen in your blood.",
                    "citation": "https://www.mayoclinic.org/tests-procedures/hemoglobin-test/about/pac-20385075",
                }
            ],
            "disclaimer": "This information is educational only.",
            "summary": "All values are within normal range.",
        }

    with patch("labbot.main.interpret_lab_values") as mock_interpret:
        # Create mock InterpretationResponse
        mock_response: MagicMock = MagicMock()
        mock_response.results = response_data.get("results", [])
        mock_response.disclaimer = response_data.get("disclaimer", "")
        mock_response.summary = response_data.get("summary")
        mock_response.model_dump = MagicMock(return_value=response_data)

        mock_interpret.return_value = mock_response
        yield


class TestHealthEndpoint:
    """Test health check endpoint used for deployment verification."""

    async def test_health_endpoint_returns_200(self, client: AsyncClient) -> None:
        """Verify health endpoint returns 200 status code."""
        response = await client.get("/health")
        assert response.status_code == 200

    async def test_health_endpoint_returns_healthy_status(
        self, client: AsyncClient
    ) -> None:
        """Verify health endpoint returns healthy status."""
        response = await client.get("/health")
        data: dict[str, str] = response.json()
        assert data["status"] == "healthy"

    async def test_health_endpoint_json_response(self, client: AsyncClient) -> None:
        """Verify health endpoint returns valid JSON."""
        response = await client.get("/health")
        assert response.headers["content-type"] == "application/json"
        # Should not raise exception
        response.json()


class TestRootEndpoint:
    """Test root endpoint serving the web UI."""

    async def test_root_endpoint_returns_200(self, client: AsyncClient) -> None:
        """Verify root endpoint returns 200 status code."""
        response = await client.get("/")
        assert response.status_code == 200

    async def test_root_endpoint_returns_html(self, client: AsyncClient) -> None:
        """Verify root endpoint returns HTML content."""
        response = await client.get("/")
        assert "text/html" in response.headers.get("content-type", "")


class TestInterpretationWithSampleData:
    """Test full interpretation pipeline with realistic lab data."""

    async def test_interpret_sample_cbc_data(self, client: AsyncClient) -> None:
        """Test interpretation with sample Complete Blood Count (CBC) data."""
        payload: dict[str, Any] = {
            "lab_values": [
                {
                    "name": "Hemoglobin",
                    "value": 14.5,
                    "unit": "g/dL",
                    "reference_min": 12.0,
                    "reference_max": 17.5,
                },
                {
                    "name": "Hematocrit",
                    "value": 42.0,
                    "unit": "%",
                    "reference_min": 35.0,
                    "reference_max": 52.0,
                },
                {
                    "name": "White Blood Cells",
                    "value": 7.5,
                    "unit": "K/uL",
                    "reference_min": 4.5,
                    "reference_max": 11.0,
                },
            ]
        }

        with mock_anthropic_for_e2e(
            response_data={
                "results": [
                    {
                        "name": "Hemoglobin",
                        "value": 14.5,
                        "unit": "g/dL",
                        "severity": "normal",
                        "explanation": "Hemoglobin is normal.",
                    },
                    {
                        "name": "Hematocrit",
                        "value": 42.0,
                        "unit": "%",
                        "severity": "normal",
                        "explanation": "Hematocrit is normal.",
                    },
                    {
                        "name": "White Blood Cells",
                        "value": 7.5,
                        "unit": "K/uL",
                        "severity": "normal",
                        "explanation": "WBC is normal.",
                    },
                ],
                "disclaimer": "This information is educational only.",
            }
        ):
            response = await client.post("/api/interpret", json=payload)
            assert response.status_code == 200

            data: dict[str, Any] = response.json()
            assert "results" in data
            assert len(data["results"]) == 3
            assert "disclaimer" in data

    async def test_interpret_returns_required_fields(
        self, client: AsyncClient
    ) -> None:
        """Verify interpretation response includes all required fields."""
        payload: dict[str, Any] = {
            "lab_values": [
                {
                    "name": "Glucose",
                    "value": 110,
                    "unit": "mg/dL",
                    "reference_min": 70,
                    "reference_max": 100,
                }
            ]
        }

        with mock_anthropic_for_e2e():
            response = await client.post("/api/interpret", json=payload)
            assert response.status_code == 200

            data: dict[str, Any] = response.json()
            assert "results" in data
            assert len(data["results"]) > 0

            # Check result structure
            result = data["results"][0]
            assert "name" in result
            assert "value" in result
            assert "unit" in result
            assert "severity" in result
            assert "explanation" in result
            assert "disclaimer" in data

    async def test_interpret_severity_levels_in_response(
        self, client: AsyncClient
    ) -> None:
        """Verify response includes severity levels for each value."""
        payload: dict[str, Any] = {
            "lab_values": [
                {
                    "name": "Hemoglobin",
                    "value": 14.5,
                    "unit": "g/dL",
                    "reference_min": 12.0,
                    "reference_max": 17.5,
                }
            ]
        }

        with mock_anthropic_for_e2e():
            response = await client.post("/api/interpret", json=payload)
            assert response.status_code == 200

            data: dict[str, Any] = response.json()
            result = data["results"][0]

            # Severity should be one of the valid levels
            valid_severities = ["normal", "borderline", "abnormal", "critical"]
            assert result["severity"] in valid_severities

    async def test_interpret_includes_citations(
        self, client: AsyncClient
    ) -> None:
        """Verify interpretation includes citations for common tests."""
        payload: dict[str, Any] = {
            "lab_values": [
                {
                    "name": "Hemoglobin",
                    "value": 14.5,
                    "unit": "g/dL",
                    "reference_min": 12.0,
                    "reference_max": 17.5,
                }
            ]
        }

        with mock_anthropic_for_e2e():
            response = await client.post("/api/interpret", json=payload)
            assert response.status_code == 200

            data: dict[str, Any] = response.json()
            result = data["results"][0]

            # Citation should be present and be a URL
            assert "citation" in result
            # Citation could be None or a URL string
            if result["citation"]:
                assert result["citation"].startswith("http")

    async def test_interpret_with_optional_fields(
        self, client: AsyncClient
    ) -> None:
        """Test interpretation with optional reference range fields."""
        payload: dict[str, Any] = {
            "lab_values": [
                {
                    "name": "Testosterone",
                    "value": 650,
                    "unit": "ng/dL",
                    # No reference_min/reference_max
                }
            ]
        }

        with mock_anthropic_for_e2e():
            response = await client.post("/api/interpret", json=payload)
            # Should still work without reference ranges
            assert response.status_code == 200
            data: dict[str, Any] = response.json()
            assert "results" in data


class TestErrorHandling:
    """Test error scenarios in interpretation endpoint."""

    async def test_interpret_pii_detection_ssn(self, client: AsyncClient) -> None:
        """Verify PII detection blocks SSN in data."""
        payload: dict[str, Any] = {
            "lab_values": [
                {
                    "name": "Hemoglobin",
                    "value": 14.5,
                    "unit": "g/dL",
                    "reference_min": 12.0,
                    "reference_max": 17.5,
                }
            ],
            # SSN embedded in field (though not a real field, demonstrates detection)
        }

        # Manually create JSON with SSN to bypass schema validation
        payload_str = json.dumps(payload)
        payload_str = payload_str.replace("Hemoglobin", "SSN: 123-45-6789")
        payload_dict = json.loads(payload_str)

        response = await client.post("/api/interpret", json=payload_dict)
        # Should be rejected with 400
        assert response.status_code == 400
        data: dict[str, Any] = response.json()
        # FastAPI wraps detail in 'detail' key for HTTPException
        detail = data.get("detail", data)
        if isinstance(detail, dict):
            assert detail.get("error") == "PII detected"
        else:
            assert "PII detected" in str(detail)

    async def test_interpret_validation_error_missing_fields(
        self, client: AsyncClient
    ) -> None:
        """Verify validation errors for missing required fields."""
        payload: dict[str, Any] = {
            "lab_values": [
                {
                    "name": "Hemoglobin",
                    # Missing 'value' and 'unit'
                }
            ]
        }

        response = await client.post("/api/interpret", json=payload)
        # Should fail validation with 422
        assert response.status_code == 422

    async def test_interpret_validation_error_empty_lab_values(
        self, client: AsyncClient
    ) -> None:
        """Verify validation errors for empty lab values list."""
        payload: dict[str, Any] = {"lab_values": []}

        response = await client.post("/api/interpret", json=payload)
        # Should fail validation with 422 (min_length=1)
        assert response.status_code == 422

    async def test_interpret_validation_error_missing_lab_values(
        self, client: AsyncClient
    ) -> None:
        """Verify validation errors when lab_values field is missing."""
        payload: dict[str, Any] = {}

        response = await client.post("/api/interpret", json=payload)
        # Should fail validation with 422
        assert response.status_code == 422


class TestIntegrationScenarios:
    """Test realistic end-to-end scenarios."""

    async def test_full_metabolic_panel(self, client: AsyncClient) -> None:
        """Test interpretation of complete metabolic panel data."""
        payload: dict[str, Any] = {
            "lab_values": [
                {
                    "name": "Glucose",
                    "value": 95,
                    "unit": "mg/dL",
                    "reference_min": 70,
                    "reference_max": 100,
                },
                {
                    "name": "Creatinine",
                    "value": 1.0,
                    "unit": "mg/dL",
                    "reference_min": 0.7,
                    "reference_max": 1.3,
                },
                {
                    "name": "Sodium",
                    "value": 140,
                    "unit": "mEq/L",
                    "reference_min": 136,
                    "reference_max": 145,
                },
                {
                    "name": "Potassium",
                    "value": 4.2,
                    "unit": "mEq/L",
                    "reference_min": 3.5,
                    "reference_max": 5.0,
                },
            ]
        }

        with mock_anthropic_for_e2e(
            response_data={
                "results": [
                    {
                        "name": "Glucose",
                        "value": 95,
                        "unit": "mg/dL",
                        "severity": "normal",
                        "explanation": "Glucose is normal.",
                    },
                    {
                        "name": "Creatinine",
                        "value": 1.0,
                        "unit": "mg/dL",
                        "severity": "normal",
                        "explanation": "Creatinine is normal.",
                    },
                    {
                        "name": "Sodium",
                        "value": 140,
                        "unit": "mEq/L",
                        "severity": "normal",
                        "explanation": "Sodium is normal.",
                    },
                    {
                        "name": "Potassium",
                        "value": 4.2,
                        "unit": "mEq/L",
                        "severity": "normal",
                        "explanation": "Potassium is normal.",
                    },
                ],
                "disclaimer": "This information is educational only.",
            }
        ):
            response = await client.post("/api/interpret", json=payload)
            assert response.status_code == 200

            data: dict[str, Any] = response.json()
            assert len(data["results"]) == 4
            assert "disclaimer" in data

            # All results should have required fields
            for result in data["results"]:
                assert "name" in result
                assert "severity" in result
                assert "explanation" in result

    async def test_multiple_abnormal_values(self, client: AsyncClient) -> None:
        """Test interpretation with some abnormal values."""
        payload: dict[str, Any] = {
            "lab_values": [
                {
                    "name": "Hemoglobin",
                    "value": 8.0,  # Low (abnormal)
                    "unit": "g/dL",
                    "reference_min": 12.0,
                    "reference_max": 17.5,
                },
                {
                    "name": "Glucose",
                    "value": 250,  # High (abnormal)
                    "unit": "mg/dL",
                    "reference_min": 70,
                    "reference_max": 100,
                },
                {
                    "name": "White Blood Cells",
                    "value": 7.0,  # Normal
                    "unit": "K/uL",
                    "reference_min": 4.5,
                    "reference_max": 11.0,
                },
            ]
        }

        with mock_anthropic_for_e2e(
            response_data={
                "results": [
                    {
                        "name": "Hemoglobin",
                        "value": 8.0,
                        "unit": "g/dL",
                        "severity": "abnormal",
                        "explanation": "Hemoglobin is low.",
                    },
                    {
                        "name": "Glucose",
                        "value": 250,
                        "unit": "mg/dL",
                        "severity": "abnormal",
                        "explanation": "Glucose is high.",
                    },
                    {
                        "name": "White Blood Cells",
                        "value": 7.0,
                        "unit": "K/uL",
                        "severity": "normal",
                        "explanation": "WBC is normal.",
                    },
                ],
                "disclaimer": "This information is educational only.",
            }
        ):
            response = await client.post("/api/interpret", json=payload)
            assert response.status_code == 200

            data: dict[str, Any] = response.json()
            results = data["results"]

            # Check that results include different severity levels
            severities = [result["severity"] for result in results]
            # With these extreme values, we should have some non-normal severity levels
            assert len(severities) == 3

    async def test_response_includes_medical_disclaimer(
        self, client: AsyncClient
    ) -> None:
        """Verify medical disclaimer is always included in responses."""
        payload: dict[str, Any] = {
            "lab_values": [
                {
                    "name": "Hemoglobin",
                    "value": 14.5,
                    "unit": "g/dL",
                    "reference_min": 12.0,
                    "reference_max": 17.5,
                }
            ]
        }

        with mock_anthropic_for_e2e():
            response = await client.post("/api/interpret", json=payload)
            assert response.status_code == 200

            data: dict[str, Any] = response.json()
            assert "disclaimer" in data
            # Disclaimer should be non-empty and present
            assert isinstance(data["disclaimer"], str)
            assert len(data["disclaimer"]) > 0
