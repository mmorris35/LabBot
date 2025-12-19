"""Test API endpoints."""

import json
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from labbot.main import app


@contextmanager
def mock_anthropic_for_endpoint(
    response_text: str,
) -> Iterator[None]:
    """Context manager for mocking Anthropic client in endpoint tests.

    Args:
        response_text: The JSON response text to return from Claude API.

    Yields:
        None (context manager setup and teardown).
    """
    with patch("labbot.main.interpret_lab_values") as mock_interpret:
        # Parse the mock response to extract results for verification
        response_data: dict[str, Any] = json.loads(response_text)

        # Create a mock InterpretationResponse
        mock_response: MagicMock = MagicMock()
        mock_response.results = response_data.get("results", [])
        mock_response.disclaimer = response_data.get("disclaimer", "")
        mock_response.summary = response_data.get("summary")

        # Make the mock iterable for JSON serialization
        mock_response.model_dump = MagicMock(
            return_value=response_data
        )

        mock_interpret.return_value = mock_response
        yield


@pytest.fixture
async def client() -> AsyncClient:
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client


async def test_root(client: AsyncClient) -> None:
    """Test root endpoint serves HTML UI."""
    response = await client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "LabBot" in response.text
    assert "<html" in response.text


async def test_health(client: AsyncClient) -> None:
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


class TestInterpretEndpoint:
    """Tests for POST /api/interpret endpoint."""

    async def test_interpret_valid_input(self, client: AsyncClient) -> None:
        """Test interpretation with valid lab results input."""
        mock_response_text: str = json.dumps(
            {
                "results": [
                    {
                        "name": "Hemoglobin",
                        "value": 14.5,
                        "unit": "g/dL",
                        "severity": "normal",
                        "explanation": (
                            "Your hemoglobin level is normal and indicates good "
                            "oxygen carrying capacity."
                        ),
                        "citation": "Mayo Clinic - Complete Blood Count",
                    }
                ],
                "disclaimer": "Always consult with a healthcare provider for medical advice.",
                "summary": "Your hemoglobin level is normal.",
            }
        )

        with mock_anthropic_for_endpoint(mock_response_text):
            payload = {
                "lab_values": [
                    {
                        "name": "Hemoglobin",
                        "value": 14.5,
                        "unit": "g/dL",
                        "reference_min": 13.5,
                        "reference_max": 17.5,
                    }
                ]
            }
            response = await client.post("/api/interpret", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert "results" in data
            assert "disclaimer" in data
            assert len(data["results"]) == 1
            assert data["results"][0]["name"] == "Hemoglobin"
            assert data["results"][0]["severity"] == "normal"

    async def test_interpret_multiple_values(self, client: AsyncClient) -> None:
        """Test interpretation with multiple lab values."""
        mock_response_text: str = json.dumps(
            {
                "results": [
                    {
                        "name": "Hemoglobin",
                        "value": 14.5,
                        "unit": "g/dL",
                        "severity": "normal",
                        "explanation": "Your hemoglobin is normal.",
                        "citation": "Mayo Clinic",
                    },
                    {
                        "name": "White Blood Cell Count",
                        "value": 7.2,
                        "unit": "10^3/µL",
                        "severity": "normal",
                        "explanation": "Your WBC count is normal.",
                        "citation": "NIH",
                    },
                ],
                "disclaimer": "Always consult with a healthcare provider for medical advice.",
                "summary": "All values are normal.",
            }
        )

        with mock_anthropic_for_endpoint(mock_response_text):
            payload = {
                "lab_values": [
                    {
                        "name": "Hemoglobin",
                        "value": 14.5,
                        "unit": "g/dL",
                        "reference_min": 13.5,
                        "reference_max": 17.5,
                    },
                    {
                        "name": "White Blood Cell Count",
                        "value": 7.2,
                        "unit": "10^3/µL",
                        "reference_min": 4.5,
                        "reference_max": 11.0,
                    },
                ]
            }
            response = await client.post("/api/interpret", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert len(data["results"]) == 2

    async def test_interpret_missing_lab_values(self, client: AsyncClient) -> None:
        """Test validation error when lab_values field is missing."""
        payload = {}
        response = await client.post("/api/interpret", json=payload)
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        errors = data["detail"]
        assert len(errors) > 0
        assert any("lab_values" in str(error) for error in errors)

    async def test_interpret_empty_lab_values(self, client: AsyncClient) -> None:
        """Test validation error when lab_values list is empty."""
        payload = {"lab_values": []}
        response = await client.post("/api/interpret", json=payload)
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_interpret_missing_required_field(self, client: AsyncClient) -> None:
        """Test validation error when required field in lab value is missing."""
        payload = {
            "lab_values": [
                {
                    "name": "Hemoglobin",
                    "unit": "g/dL",
                    # Missing "value" field
                }
            ]
        }
        response = await client.post("/api/interpret", json=payload)
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        errors = data["detail"]
        assert len(errors) > 0
        assert any("value" in str(error) for error in errors)

    async def test_interpret_invalid_type(self, client: AsyncClient) -> None:
        """Test validation error when field has wrong type."""
        payload = {
            "lab_values": [
                {
                    "name": "Hemoglobin",
                    "value": "fourteen point five",  # Should be float
                    "unit": "g/dL",
                }
            ]
        }
        response = await client.post("/api/interpret", json=payload)
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_interpret_invalid_json(self, client: AsyncClient) -> None:
        """Test validation error with malformed JSON."""
        response = await client.post(
            "/api/interpret",
            content="{invalid json}",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422

    async def test_interpret_optional_fields(self, client: AsyncClient) -> None:
        """Test that optional fields (reference_min, reference_max) are not required."""
        mock_response_text: str = json.dumps(
            {
                "results": [
                    {
                        "name": "Hemoglobin",
                        "value": 14.5,
                        "unit": "g/dL",
                        "severity": "normal",
                        "explanation": "Test explanation",
                        "citation": "Source",
                    }
                ],
                "disclaimer": "Disclaimer here.",
            }
        )

        with mock_anthropic_for_endpoint(mock_response_text):
            payload = {
                "lab_values": [
                    {
                        "name": "Hemoglobin",
                        "value": 14.5,
                        "unit": "g/dL",
                        # reference_min and reference_max are optional
                    }
                ]
            }
            response = await client.post("/api/interpret", json=payload)
            assert response.status_code == 200

    async def test_interpret_max_lab_values(self, client: AsyncClient) -> None:
        """Test that up to 50 lab values are accepted."""
        # Create mock response with 50 results
        results = [
            {
                "name": f"Test{index}",
                "value": 10.0 + index,
                "unit": "unit",
                "severity": "normal",
                "explanation": "Test explanation",
                "citation": "Source",
            }
            for index in range(50)
        ]
        mock_response_text: str = json.dumps(
            {
                "results": results,
                "disclaimer": "Disclaimer here.",
            }
        )

        with mock_anthropic_for_endpoint(mock_response_text):
            lab_values = [
                {
                    "name": f"Test{index}",
                    "value": 10.0 + index,
                    "unit": "unit",
                }
                for index in range(50)
            ]
            payload = {"lab_values": lab_values}
            response = await client.post("/api/interpret", json=payload)
            assert response.status_code == 200

    async def test_interpret_exceeds_max_lab_values(self, client: AsyncClient) -> None:
        """Test validation error when exceeding max 50 lab values."""
        lab_values = [
            {
                "name": f"Test{index}",
                "value": 10.0 + index,
                "unit": "unit",
            }
            for index in range(51)
        ]
        payload = {"lab_values": lab_values}
        response = await client.post("/api/interpret", json=payload)
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_interpret_pii_detection_ssn(self, client: AsyncClient) -> None:
        """Test that request with SSN in name field is rejected with 400."""
        payload = {
            "lab_values": [
                {
                    "name": "Hemoglobin SSN: 123-45-6789",
                    "value": 14.5,
                    "unit": "g/dL",
                }
            ]
        }
        response = await client.post("/api/interpret", json=payload)
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "PII detected"
        assert "ssn" in data["detail"]["types"]

    async def test_interpret_pii_detection_phone(self, client: AsyncClient) -> None:
        """Test that request with phone number is rejected with 400."""
        payload = {
            "lab_values": [
                {
                    "name": "Patient contact: 555-123-4567",
                    "value": 123.0,
                    "unit": "identifier",
                }
            ]
        }
        response = await client.post("/api/interpret", json=payload)
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "PII detected"
        assert "phone" in data["detail"]["types"]

    async def test_interpret_pii_detection_email(self, client: AsyncClient) -> None:
        """Test that request with email is rejected with 400."""
        payload = {
            "lab_values": [
                {
                    "name": "Patient email: patient@example.com",
                    "value": 123.0,
                    "unit": "contact",
                }
            ]
        }
        response = await client.post("/api/interpret", json=payload)
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "PII detected"
        assert "email" in data["detail"]["types"]

    async def test_interpret_pii_detection_multiple_types(self, client: AsyncClient) -> None:
        """Test that multiple PII types are all reported."""
        payload = {
            "lab_values": [
                {
                    "name": "Contact: john@example.com, phone 555-123-4567",
                    "value": 123.0,
                    "unit": "mixed",
                }
            ]
        }
        response = await client.post("/api/interpret", json=payload)
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "PII detected"
        detected_types = data["detail"]["types"]
        assert "email" in detected_types
        assert "phone" in detected_types

    async def test_interpret_pii_detection_dob(self, client: AsyncClient) -> None:
        """Test that request with date of birth is rejected with 400."""
        payload = {
            "lab_values": [
                {
                    "name": "Patient DOB 12/31/1990",
                    "value": 123.0,
                    "unit": "date",
                }
            ]
        }
        response = await client.post("/api/interpret", json=payload)
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "PII detected"
        assert "dob" in data["detail"]["types"]

    async def test_interpret_pii_detection_name_field(self, client: AsyncClient) -> None:
        """Test that request with name field pattern is rejected with 400."""
        payload = {
            "lab_values": [
                {
                    "name": "patient_name: John Smith",
                    "value": 123.0,
                    "unit": "test",
                }
            ]
        }
        response = await client.post("/api/interpret", json=payload)
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "PII detected"
        assert "name" in data["detail"]["types"]

    async def test_interpret_clean_data_accepted(self, client: AsyncClient) -> None:
        """Test that clean data without PII is accepted and interpreted."""
        mock_response_text: str = json.dumps(
            {
                "results": [
                    {
                        "name": "Hemoglobin",
                        "value": 14.5,
                        "unit": "g/dL",
                        "severity": "normal",
                        "explanation": "Your hemoglobin is normal.",
                        "citation": "Mayo Clinic",
                    },
                    {
                        "name": "White Blood Cell Count",
                        "value": 7.2,
                        "unit": "10^3/µL",
                        "severity": "normal",
                        "explanation": "Your WBC count is normal.",
                        "citation": "NIH",
                    },
                ],
                "disclaimer": "Always consult with a healthcare provider for medical advice.",
                "summary": "All values are normal.",
            }
        )

        with mock_anthropic_for_endpoint(mock_response_text):
            payload = {
                "lab_values": [
                    {
                        "name": "Hemoglobin",
                        "value": 14.5,
                        "unit": "g/dL",
                        "reference_min": 13.5,
                        "reference_max": 17.5,
                    },
                    {
                        "name": "White Blood Cell Count",
                        "value": 7.2,
                        "unit": "10^3/µL",
                        "reference_min": 4.5,
                        "reference_max": 11.0,
                    },
                ]
            }
            response = await client.post("/api/interpret", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert "results" in data
            assert "disclaimer" in data
            assert len(data["results"]) == 2

    async def test_interpret_api_error_returns_503(self, client: AsyncClient) -> None:
        """Test that Claude API error returns 503 Service Unavailable."""
        from anthropic import APIError

        with patch("labbot.main.interpret_lab_values") as mock_interpret:
            # Create APIError with proper arguments (message, request, body)
            mock_error = APIError(
                "API rate limit exceeded",
                request=MagicMock(),
                body={"error": "rate_limit_exceeded"}
            )
            mock_interpret.side_effect = mock_error

            payload = {
                "lab_values": [
                    {
                        "name": "Hemoglobin",
                        "value": 14.5,
                        "unit": "g/dL",
                    }
                ]
            }
            response = await client.post("/api/interpret", json=payload)
            assert response.status_code == 503
            data = response.json()
            assert "detail" in data
            assert "API error" in data["detail"]

    async def test_interpret_invalid_json_response_returns_503(
        self, client: AsyncClient
    ) -> None:
        """Test that invalid JSON in Claude response returns 503."""
        with patch("labbot.main.interpret_lab_values") as mock_interpret:
            mock_interpret.side_effect = ValueError("Claude API returned invalid JSON")

            payload = {
                "lab_values": [
                    {
                        "name": "Hemoglobin",
                        "value": 14.5,
                        "unit": "g/dL",
                    }
                ]
            }
            response = await client.post("/api/interpret", json=payload)
            assert response.status_code == 503
            data = response.json()
            assert "detail" in data
            assert "process lab interpretation" in data["detail"]

    async def test_interpret_response_includes_all_fields(
        self, client: AsyncClient
    ) -> None:
        """Test that interpretation response includes all required fields."""
        mock_response_text: str = json.dumps(
            {
                "results": [
                    {
                        "name": "Glucose",
                        "value": 95.0,
                        "unit": "mg/dL",
                        "severity": "normal",
                        "explanation": "Fasting glucose is in the normal range.",
                        "citation": "MedlinePlus - Blood Sugar",
                    }
                ],
                "disclaimer": "This is educational information only.",
                "summary": "Glucose level is normal.",
            }
        )

        with mock_anthropic_for_endpoint(mock_response_text):
            payload = {
                "lab_values": [
                    {
                        "name": "Glucose",
                        "value": 95.0,
                        "unit": "mg/dL",
                        "reference_min": 70.0,
                        "reference_max": 100.0,
                    }
                ]
            }
            response = await client.post("/api/interpret", json=payload)
            assert response.status_code == 200
            data = response.json()

            # Verify all required fields in response
            assert "results" in data
            assert "disclaimer" in data
            assert len(data["results"]) == 1

            result = data["results"][0]
            # Verify all required fields in each result
            assert result["name"] == "Glucose"
            assert result["value"] == 95.0
            assert result["unit"] == "mg/dL"
            assert result["severity"] == "normal"
            assert result["explanation"] == "Fasting glucose is in the normal range."
            assert result["citation"] == "MedlinePlus - Blood Sugar"

            # Verify disclaimer is present
            assert "This is educational information only." in data["disclaimer"]

            # Verify optional summary is present
            assert "summary" in data
            assert data["summary"] == "Glucose level is normal."

    async def test_interpret_severity_levels_preserved(
        self, client: AsyncClient
    ) -> None:
        """Test that different severity levels are correctly preserved."""
        mock_response_text: str = json.dumps(
            {
                "results": [
                    {
                        "name": "Test Normal",
                        "value": 100.0,
                        "unit": "unit",
                        "severity": "normal",
                        "explanation": "This is normal.",
                        "citation": "Source",
                    },
                    {
                        "name": "Test Borderline",
                        "value": 105.0,
                        "unit": "unit",
                        "severity": "borderline",
                        "explanation": "This is borderline.",
                        "citation": "Source",
                    },
                    {
                        "name": "Test Abnormal",
                        "value": 110.0,
                        "unit": "unit",
                        "severity": "abnormal",
                        "explanation": "This is abnormal.",
                        "citation": "Source",
                    },
                    {
                        "name": "Test Critical",
                        "value": 120.0,
                        "unit": "unit",
                        "severity": "critical",
                        "explanation": "This is critical.",
                        "citation": "Source",
                    },
                ],
                "disclaimer": "Disclaimer here.",
            }
        )

        with mock_anthropic_for_endpoint(mock_response_text):
            payload = {
                "lab_values": [
                    {
                        "name": "Test Normal",
                        "value": 100.0,
                        "unit": "unit",
                    },
                    {
                        "name": "Test Borderline",
                        "value": 105.0,
                        "unit": "unit",
                    },
                    {
                        "name": "Test Abnormal",
                        "value": 110.0,
                        "unit": "unit",
                    },
                    {
                        "name": "Test Critical",
                        "value": 120.0,
                        "unit": "unit",
                    },
                ]
            }
            response = await client.post("/api/interpret", json=payload)
            assert response.status_code == 200
            data = response.json()

            severities = [result["severity"] for result in data["results"]]
            assert "normal" in severities
            assert "borderline" in severities
            assert "abnormal" in severities
            assert "critical" in severities

    async def test_interpret_citations_included(self, client: AsyncClient) -> None:
        """Test that citations are included in response."""
        mock_response_text: str = json.dumps(
            {
                "results": [
                    {
                        "name": "Test 1",
                        "value": 100.0,
                        "unit": "unit",
                        "severity": "normal",
                        "explanation": "Explanation 1",
                        "citation": "Mayo Clinic - Test 1",
                    },
                    {
                        "name": "Test 2",
                        "value": 200.0,
                        "unit": "unit",
                        "severity": "normal",
                        "explanation": "Explanation 2",
                        "citation": "NIH - Test 2",
                    },
                ],
                "disclaimer": "Disclaimer here.",
            }
        )

        with mock_anthropic_for_endpoint(mock_response_text):
            payload = {
                "lab_values": [
                    {"name": "Test 1", "value": 100.0, "unit": "unit"},
                    {"name": "Test 2", "value": 200.0, "unit": "unit"},
                ]
            }
            response = await client.post("/api/interpret", json=payload)
            assert response.status_code == 200
            data = response.json()

            citations = [result.get("citation") for result in data["results"]]
            assert "Mayo Clinic - Test 1" in citations
            assert "NIH - Test 2" in citations

    async def test_interpret_disclaimer_always_present(
        self, client: AsyncClient
    ) -> None:
        """Test that medical disclaimer is always included in response."""
        mock_response_text: str = json.dumps(
            {
                "results": [
                    {
                        "name": "Test",
                        "value": 100.0,
                        "unit": "unit",
                        "severity": "normal",
                        "explanation": "Test explanation",
                        "citation": "Source",
                    }
                ],
                "disclaimer": "Always consult with a healthcare provider for medical advice.",
            }
        )

        with mock_anthropic_for_endpoint(mock_response_text):
            payload = {"lab_values": [{"name": "Test", "value": 100.0, "unit": "unit"}]}
            response = await client.post("/api/interpret", json=payload)
            assert response.status_code == 200
            data = response.json()

            assert "disclaimer" in data
            assert len(data["disclaimer"]) > 0
