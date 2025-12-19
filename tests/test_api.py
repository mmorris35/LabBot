"""Test API endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient

from labbot.main import app


@pytest.fixture
async def client() -> AsyncClient:
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client


async def test_root(client: AsyncClient) -> None:
    """Test root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "LabBot API"
    assert "version" in data


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
        assert data["status"] == "processing"
        assert "message" in data

    async def test_interpret_multiple_values(self, client: AsyncClient) -> None:
        """Test interpretation with multiple lab values."""
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
        """Test that clean data without PII is accepted."""
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
        assert data["status"] == "processing"
