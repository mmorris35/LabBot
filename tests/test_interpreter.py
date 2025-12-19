"""Test Claude API interpreter module."""

import json
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest
from anthropic import APIError

from labbot.interpreter import interpret_lab_values
from labbot.schemas import InterpretationResponse, LabValue, SeverityLevel


@contextmanager
def mock_anthropic_with_api_key(
    response_text: str,
) -> Iterator[None]:
    """Context manager for mocking Anthropic client with settings.

    Args:
        response_text: The JSON response text to return from Claude API.

    Yields:
        None (context manager setup and teardown).
    """
    with patch("labbot.interpreter.settings") as mock_settings:
        mock_settings.anthropic_api_key = "test-api-key"

        with patch("labbot.interpreter.Anthropic") as mock_anthropic_class:
            mock_client: MagicMock = MagicMock()
            mock_anthropic_class.return_value = mock_client

            mock_message: MagicMock = MagicMock()
            mock_message.content[0].text = response_text
            mock_client.messages.create.return_value = mock_message

            yield


class TestInterpretLabValuesBasic:
    """Test basic interpret_lab_values functionality."""

    def test_interpret_single_lab_value_success(self) -> None:
        """Test successful interpretation of a single lab value."""
        lab_value: LabValue = LabValue(
            name="Hemoglobin",
            value=14.5,
            unit="g/dL",
            reference_min=13.5,
            reference_max=17.5,
        )

        mock_response_text: str = json.dumps(
            {
                "results": [
                    {
                        "name": "Hemoglobin",
                        "value": 14.5,
                        "unit": "g/dL",
                        "severity": "normal",
                        "explanation": (
                            "Hemoglobin is the protein in red blood cells that carries "
                            "oxygen. Your level is within the normal range, indicating "
                            "good oxygen-carrying capacity."
                        ),
                        "citation": "Mayo Clinic - Complete Blood Count",
                    }
                ],
                "disclaimer": "Always consult with a healthcare provider for medical advice.",
                "summary": "Your hemoglobin level is normal.",
            }
        )

        with mock_anthropic_with_api_key(mock_response_text):
            response: InterpretationResponse = interpret_lab_values([lab_value])

            assert isinstance(response, InterpretationResponse)
            assert len(response.results) == 1
            assert response.results[0].name == "Hemoglobin"
            assert response.results[0].severity == SeverityLevel.NORMAL
            assert "oxygen" in response.results[0].explanation.lower()
            assert "Mayo Clinic" in response.results[0].citation

    def test_interpret_multiple_lab_values_success(self) -> None:
        """Test successful interpretation of multiple lab values."""
        lab_values: list[LabValue] = [
            LabValue(
                name="Hemoglobin",
                value=14.5,
                unit="g/dL",
                reference_min=13.5,
                reference_max=17.5,
            ),
            LabValue(
                name="White Blood Cell Count",
                value=7.2,
                unit="10^3/µL",
                reference_min=4.5,
                reference_max=11.0,
            ),
        ]

        mock_response_text: str = json.dumps(
            {
                "results": [
                    {
                        "name": "Hemoglobin",
                        "value": 14.5,
                        "unit": "g/dL",
                        "severity": "normal",
                        "explanation": "Hemoglobin is normal.",
                        "citation": "Mayo Clinic",
                    },
                    {
                        "name": "White Blood Cell Count",
                        "value": 7.2,
                        "unit": "10^3/µL",
                        "severity": "normal",
                        "explanation": "WBC count is normal.",
                        "citation": "NIH",
                    },
                ],
                "disclaimer": "Always consult with a healthcare provider for medical advice.",
                "summary": "All values are normal.",
            }
        )

        with mock_anthropic_with_api_key(mock_response_text):
            response: InterpretationResponse = interpret_lab_values(lab_values)

            assert len(response.results) == 2
            assert response.results[0].name == "Hemoglobin"
            assert response.results[1].name == "White Blood Cell Count"

    def test_interpret_with_optional_fields(self) -> None:
        """Test interpretation with optional citation and summary."""
        lab_value: LabValue = LabValue(
            name="Test Value",
            value=10.0,
            unit="unit",
        )

        mock_response_text: str = json.dumps(
            {
                "results": [
                    {
                        "name": "Test Value",
                        "value": 10.0,
                        "unit": "unit",
                        "severity": "normal",
                        "explanation": "Test explanation.",
                        "citation": None,
                    }
                ],
                "disclaimer": "Always consult.",
                "summary": None,
            }
        )

        with mock_anthropic_with_api_key(mock_response_text):
            response: InterpretationResponse = interpret_lab_values([lab_value])

            assert response.results[0].citation is None
            assert response.summary is None

    def test_interpret_without_reference_range(self) -> None:
        """Test interpretation with lab values missing reference ranges."""
        lab_value: LabValue = LabValue(
            name="Custom Test",
            value=42.0,
            unit="custom_unit",
            reference_min=None,
            reference_max=None,
        )

        mock_response_text: str = json.dumps(
            {
                "results": [
                    {
                        "name": "Custom Test",
                        "value": 42.0,
                        "unit": "custom_unit",
                        "severity": "normal",
                        "explanation": "No reference range available.",
                        "citation": "Reference source",
                    }
                ],
                "disclaimer": "Consult healthcare provider.",
                "summary": None,
            }
        )

        with mock_anthropic_with_api_key(mock_response_text):
            response: InterpretationResponse = interpret_lab_values([lab_value])

            assert response.results[0].value == 42.0


class TestInterpretLabValuesSeverity:
    """Test severity level interpretation."""

    def test_interpret_normal_severity(self) -> None:
        """Test interpretation of normal severity level."""
        lab_value: LabValue = LabValue(
            name="Test",
            value=10.0,
            unit="unit",
            reference_min=5.0,
            reference_max=15.0,
        )

        mock_response_text: str = json.dumps(
            {
                "results": [
                    {
                        "name": "Test",
                        "value": 10.0,
                        "unit": "unit",
                        "severity": "normal",
                        "explanation": "Value is normal.",
                        "citation": "Source",
                    }
                ],
                "disclaimer": "Consult.",
            }
        )

        with mock_anthropic_with_api_key(mock_response_text):
            response: InterpretationResponse = interpret_lab_values([lab_value])

            assert response.results[0].severity == SeverityLevel.NORMAL

    def test_interpret_borderline_severity(self) -> None:
        """Test interpretation of borderline severity level."""
        lab_value: LabValue = LabValue(
            name="Test",
            value=14.8,
            unit="unit",
            reference_min=10.0,
            reference_max=15.0,
        )

        mock_response_text: str = json.dumps(
            {
                "results": [
                    {
                        "name": "Test",
                        "value": 14.8,
                        "unit": "unit",
                        "severity": "borderline",
                        "explanation": "Value is slightly elevated.",
                        "citation": "Source",
                    }
                ],
                "disclaimer": "Consult.",
            }
        )

        with mock_anthropic_with_api_key(mock_response_text):
            response: InterpretationResponse = interpret_lab_values([lab_value])

            assert response.results[0].severity == SeverityLevel.BORDERLINE

    def test_interpret_abnormal_severity(self) -> None:
        """Test interpretation of abnormal severity level."""
        lab_value: LabValue = LabValue(
            name="Test",
            value=25.0,
            unit="unit",
            reference_min=10.0,
            reference_max=15.0,
        )

        mock_response_text: str = json.dumps(
            {
                "results": [
                    {
                        "name": "Test",
                        "value": 25.0,
                        "unit": "unit",
                        "severity": "abnormal",
                        "explanation": "Value is significantly elevated.",
                        "citation": "Source",
                    }
                ],
                "disclaimer": "Consult.",
            }
        )

        with mock_anthropic_with_api_key(mock_response_text):
            response: InterpretationResponse = interpret_lab_values([lab_value])

            assert response.results[0].severity == SeverityLevel.ABNORMAL

    def test_interpret_critical_severity(self) -> None:
        """Test interpretation of critical severity level."""
        lab_value: LabValue = LabValue(
            name="Test",
            value=50.0,
            unit="unit",
            reference_min=10.0,
            reference_max=15.0,
        )

        mock_response_text: str = json.dumps(
            {
                "results": [
                    {
                        "name": "Test",
                        "value": 50.0,
                        "unit": "unit",
                        "severity": "critical",
                        "explanation": "Value is critically elevated.",
                        "citation": "Source",
                    }
                ],
                "disclaimer": "Consult immediately.",
            }
        )

        with mock_anthropic_with_api_key(mock_response_text):
            response: InterpretationResponse = interpret_lab_values([lab_value])

            assert response.results[0].severity == SeverityLevel.CRITICAL


class TestInterpretLabValuesAPIErrors:
    """Test error handling for API failures."""

    def test_api_error_raises_exception(self) -> None:
        """Test that API errors are raised to caller."""
        lab_value: LabValue = LabValue(
            name="Test",
            value=10.0,
            unit="unit",
        )

        with patch("labbot.interpreter.settings") as mock_settings:
            mock_settings.anthropic_api_key = "test-api-key"

            with patch("labbot.interpreter.Anthropic") as mock_anthropic_class:
                mock_client: MagicMock = MagicMock()
                mock_anthropic_class.return_value = mock_client

                # Simulate API error
                mock_client.messages.create.side_effect = APIError(
                    message="API Error",
                    request=Mock(),
                    body={"error": "test error"},
                )

                with pytest.raises(APIError):
                    interpret_lab_values([lab_value])

    def test_invalid_json_response_raises_error(self) -> None:
        """Test that invalid JSON response raises ValueError."""
        lab_value: LabValue = LabValue(
            name="Test",
            value=10.0,
            unit="unit",
        )

        with patch("labbot.interpreter.settings") as mock_settings:
            mock_settings.anthropic_api_key = "test-api-key"

            with patch("labbot.interpreter.Anthropic") as mock_anthropic_class:
                mock_client: MagicMock = MagicMock()
                mock_anthropic_class.return_value = mock_client

                mock_message: MagicMock = MagicMock()
                mock_message.content[0].text = "This is not valid JSON {"
                mock_client.messages.create.return_value = mock_message

                with pytest.raises(ValueError, match="Claude API returned invalid JSON"):
                    interpret_lab_values([lab_value])

    def test_missing_api_key_raises_error(self) -> None:
        """Test that missing API key raises ValueError."""
        lab_value: LabValue = LabValue(
            name="Test",
            value=10.0,
            unit="unit",
        )

        with patch("labbot.interpreter.settings") as mock_settings:
            mock_settings.anthropic_api_key = ""

            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
                interpret_lab_values([lab_value])

    def test_malformed_response_json_raises_error(self) -> None:
        """Test that malformed response JSON raises error."""
        lab_value: LabValue = LabValue(
            name="Test",
            value=10.0,
            unit="unit",
        )

        mock_response_text: str = json.dumps(
            {
                "invalid_field": "missing required fields",
            }
        )

        with mock_anthropic_with_api_key(mock_response_text):
            with pytest.raises(ValueError):
                interpret_lab_values([lab_value])


class TestInterpretLabValuesPrompt:
    """Test prompt formatting and API call."""

    def test_correct_model_used(self) -> None:
        """Test that Claude Haiku model is used."""
        lab_value: LabValue = LabValue(
            name="Test",
            value=10.0,
            unit="unit",
        )

        mock_response_text: str = json.dumps(
            {
                "results": [
                    {
                        "name": "Test",
                        "value": 10.0,
                        "unit": "unit",
                        "severity": "normal",
                        "explanation": "Explanation",
                        "citation": "Source",
                    }
                ],
                "disclaimer": "Consult.",
            }
        )

        with patch("labbot.interpreter.settings") as mock_settings:
            mock_settings.anthropic_api_key = "test-api-key"

            with patch("labbot.interpreter.Anthropic") as mock_anthropic_class:
                mock_client: MagicMock = MagicMock()
                mock_anthropic_class.return_value = mock_client

                mock_message: MagicMock = MagicMock()
                mock_message.content[0].text = mock_response_text
                mock_client.messages.create.return_value = mock_message

                interpret_lab_values([lab_value])

                # Verify Haiku model was used
                call_args: Any = mock_client.messages.create.call_args
                assert call_args.kwargs["model"] == "claude-3-haiku-20240307"

    def test_max_tokens_set(self) -> None:
        """Test that max_tokens is set appropriately."""
        lab_value: LabValue = LabValue(
            name="Test",
            value=10.0,
            unit="unit",
        )

        mock_response_text: str = json.dumps(
            {
                "results": [
                    {
                        "name": "Test",
                        "value": 10.0,
                        "unit": "unit",
                        "severity": "normal",
                        "explanation": "Explanation",
                        "citation": "Source",
                    }
                ],
                "disclaimer": "Consult.",
            }
        )

        with patch("labbot.interpreter.settings") as mock_settings:
            mock_settings.anthropic_api_key = "test-api-key"

            with patch("labbot.interpreter.Anthropic") as mock_anthropic_class:
                mock_client: MagicMock = MagicMock()
                mock_anthropic_class.return_value = mock_client

                mock_message: MagicMock = MagicMock()
                mock_message.content[0].text = mock_response_text
                mock_client.messages.create.return_value = mock_message

                interpret_lab_values([lab_value])

                # Verify max_tokens is set
                call_args: Any = mock_client.messages.create.call_args
                assert call_args.kwargs["max_tokens"] == 2048

    def test_prompt_includes_lab_values(self) -> None:
        """Test that prompt includes formatted lab values."""
        lab_value: LabValue = LabValue(
            name="TestValue",
            value=15.5,
            unit="test_unit",
            reference_min=10.0,
            reference_max=20.0,
        )

        mock_response_text: str = json.dumps(
            {
                "results": [
                    {
                        "name": "TestValue",
                        "value": 15.5,
                        "unit": "test_unit",
                        "severity": "normal",
                        "explanation": "Explanation",
                        "citation": "Source",
                    }
                ],
                "disclaimer": "Consult.",
            }
        )

        with patch("labbot.interpreter.settings") as mock_settings:
            mock_settings.anthropic_api_key = "test-api-key"

            with patch("labbot.interpreter.Anthropic") as mock_anthropic_class:
                mock_client: MagicMock = MagicMock()
                mock_anthropic_class.return_value = mock_client

                mock_message: MagicMock = MagicMock()
                mock_message.content[0].text = mock_response_text
                mock_client.messages.create.return_value = mock_message

                interpret_lab_values([lab_value])

                # Get the prompt passed to API
                call_args: Any = mock_client.messages.create.call_args
                prompt_message: dict[str, str] = call_args.kwargs["messages"][0]
                prompt_content: str = prompt_message["content"]

                # Verify lab value is included in prompt
                assert "TestValue" in prompt_content
                assert "15.5" in prompt_content
                assert "test_unit" in prompt_content

    def test_client_initialized_with_api_key(self) -> None:
        """Test that Anthropic client is initialized with API key."""
        lab_value: LabValue = LabValue(
            name="Test",
            value=10.0,
            unit="unit",
        )

        mock_response_text: str = json.dumps(
            {
                "results": [
                    {
                        "name": "Test",
                        "value": 10.0,
                        "unit": "unit",
                        "severity": "normal",
                        "explanation": "Explanation",
                        "citation": "Source",
                    }
                ],
                "disclaimer": "Consult.",
            }
        )

        with patch("labbot.interpreter.settings") as mock_settings:
            mock_settings.anthropic_api_key = "test-api-key-123"

            with patch("labbot.interpreter.Anthropic") as mock_anthropic_class:
                mock_client: MagicMock = MagicMock()
                mock_anthropic_class.return_value = mock_client

                mock_message: MagicMock = MagicMock()
                mock_message.content[0].text = mock_response_text
                mock_client.messages.create.return_value = mock_message

                interpret_lab_values([lab_value])

                # Verify Anthropic was initialized with API key
                mock_anthropic_class.assert_called_with(api_key="test-api-key-123")


class TestInterpretLabValuesIntegration:
    """Integration tests with realistic scenarios."""

    def test_interpret_realistic_cbc_panel(self) -> None:
        """Test interpretation of realistic Complete Blood Count panel."""
        lab_values: list[LabValue] = [
            LabValue(
                name="Hemoglobin",
                value=14.2,
                unit="g/dL",
                reference_min=13.5,
                reference_max=17.5,
            ),
            LabValue(
                name="Hematocrit",
                value=42.0,
                unit="%",
                reference_min=41.0,
                reference_max=50.0,
            ),
            LabValue(
                name="White Blood Cell Count",
                value=7.5,
                unit="10^3/µL",
                reference_min=4.5,
                reference_max=11.0,
            ),
        ]

        mock_response_text: str = json.dumps(
            {
                "results": [
                    {
                        "name": "Hemoglobin",
                        "value": 14.2,
                        "unit": "g/dL",
                        "severity": "normal",
                        "explanation": (
                            "Hemoglobin is the protein in red blood cells that carries "
                            "oxygen. Your level indicates good oxygen transport."
                        ),
                        "citation": "Mayo Clinic - Complete Blood Count",
                    },
                    {
                        "name": "Hematocrit",
                        "value": 42.0,
                        "unit": "%",
                        "severity": "normal",
                        "explanation": (
                            "Hematocrit is the percentage of red blood cells in "
                            "blood. Your percentage is normal."
                        ),
                        "citation": "NIH - Hematocrit",
                    },
                    {
                        "name": "White Blood Cell Count",
                        "value": 7.5,
                        "unit": "10^3/µL",
                        "severity": "normal",
                        "explanation": (
                            "WBC count reflects immune system function. "
                            "Your count is normal."
                        ),
                        "citation": "MedlinePlus - White Blood Cell Count",
                    },
                ],
                "disclaimer": (
                    "Always consult with a healthcare provider for medical advice."
                ),
                "summary": "Your complete blood count is within normal ranges.",
            }
        )

        with mock_anthropic_with_api_key(mock_response_text):
            response: InterpretationResponse = interpret_lab_values(lab_values)

            assert len(response.results) == 3
            assert all(
                result.severity == SeverityLevel.NORMAL
                for result in response.results
            )
            assert "normal ranges" in response.summary.lower()

    def test_interpret_mixed_severity_results(self) -> None:
        """Test interpretation with mixed severity levels."""
        lab_values: list[LabValue] = [
            LabValue(
                name="Glucose",
                value=180.0,
                unit="mg/dL",
                reference_min=70.0,
                reference_max=100.0,
            ),
            LabValue(
                name="Cholesterol",
                value=210.0,
                unit="mg/dL",
                reference_min=None,
                reference_max=200.0,
            ),
        ]

        mock_response_text: str = json.dumps(
            {
                "results": [
                    {
                        "name": "Glucose",
                        "value": 180.0,
                        "unit": "mg/dL",
                        "severity": "abnormal",
                        "explanation": (
                            "Your glucose level is elevated, which may indicate "
                            "diabetes or prediabetes."
                        ),
                        "citation": "Mayo Clinic - Glucose Test",
                    },
                    {
                        "name": "Cholesterol",
                        "value": 210.0,
                        "unit": "mg/dL",
                        "severity": "borderline",
                        "explanation": "Your cholesterol is slightly elevated.",
                        "citation": "NIH - Cholesterol",
                    },
                ],
                "disclaimer": (
                    "Always consult with a healthcare provider for medical advice."
                ),
                "summary": "Some values are elevated. Please consult your doctor.",
            }
        )

        with mock_anthropic_with_api_key(mock_response_text):
            response: InterpretationResponse = interpret_lab_values(lab_values)

            assert response.results[0].severity == SeverityLevel.ABNORMAL
            assert response.results[1].severity == SeverityLevel.BORDERLINE
