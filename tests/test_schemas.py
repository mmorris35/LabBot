"""Test Pydantic schemas for lab results."""

import pytest
from pydantic import ValidationError

from labbot.schemas import (
    InterpretationResponse,
    InterpretedValue,
    LabResultsInput,
    LabValue,
    SeverityLevel,
)


class TestLabValue:
    """Test LabValue schema."""

    def test_valid_lab_value(self) -> None:
        """Test creating a valid lab value."""
        lab_value = LabValue(
            name="Hemoglobin",
            value=14.5,
            unit="g/dL",
            reference_min=13.5,
            reference_max=17.5,
        )
        assert lab_value.name == "Hemoglobin"
        assert lab_value.value == 14.5
        assert lab_value.unit == "g/dL"
        assert lab_value.reference_min == 13.5
        assert lab_value.reference_max == 17.5

    def test_lab_value_without_reference_range(self) -> None:
        """Test creating a lab value without reference range."""
        lab_value = LabValue(
            name="Glucose",
            value=95.0,
            unit="mg/dL",
        )
        assert lab_value.name == "Glucose"
        assert lab_value.value == 95.0
        assert lab_value.unit == "mg/dL"
        assert lab_value.reference_min is None
        assert lab_value.reference_max is None

    def test_lab_value_missing_name(self) -> None:
        """Test that missing name raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            LabValue(
                value=14.5,
                unit="g/dL",
            )
        assert "name" in str(exc_info.value)

    def test_lab_value_missing_value(self) -> None:
        """Test that missing value raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            LabValue(
                name="Hemoglobin",
                unit="g/dL",
            )
        assert "value" in str(exc_info.value)

    def test_lab_value_missing_unit(self) -> None:
        """Test that missing unit raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            LabValue(
                name="Hemoglobin",
                value=14.5,
            )
        assert "unit" in str(exc_info.value)

    def test_lab_value_empty_name(self) -> None:
        """Test that empty name raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            LabValue(
                name="",
                value=14.5,
                unit="g/dL",
            )
        assert "name" in str(exc_info.value)

    def test_lab_value_empty_unit(self) -> None:
        """Test that empty unit raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            LabValue(
                name="Hemoglobin",
                value=14.5,
                unit="",
            )
        assert "unit" in str(exc_info.value)

    def test_lab_value_negative_value(self) -> None:
        """Test that negative values are allowed (some tests can be negative)."""
        lab_value = LabValue(
            name="Temperature Change",
            value=-5.0,
            unit="°C",
        )
        assert lab_value.value == -5.0

    def test_lab_value_zero_value(self) -> None:
        """Test that zero value is allowed."""
        lab_value = LabValue(
            name="Troponin",
            value=0.0,
            unit="ng/mL",
        )
        assert lab_value.value == 0.0

    def test_lab_value_very_large_value(self) -> None:
        """Test that very large values are allowed."""
        lab_value = LabValue(
            name="Platelet Count",
            value=999999.0,
            unit="10^3/µL",
        )
        assert lab_value.value == 999999.0


class TestLabResultsInput:
    """Test LabResultsInput schema."""

    def test_valid_lab_results_single_value(self) -> None:
        """Test creating valid lab results with single value."""
        results = LabResultsInput(
            lab_values=[
                LabValue(
                    name="Hemoglobin",
                    value=14.5,
                    unit="g/dL",
                    reference_min=13.5,
                    reference_max=17.5,
                )
            ]
        )
        assert len(results.lab_values) == 1
        assert results.lab_values[0].name == "Hemoglobin"

    def test_valid_lab_results_multiple_values(self) -> None:
        """Test creating valid lab results with multiple values."""
        results = LabResultsInput(
            lab_values=[
                LabValue(
                    name="Hemoglobin",
                    value=14.5,
                    unit="g/dL",
                ),
                LabValue(
                    name="Glucose",
                    value=95.0,
                    unit="mg/dL",
                ),
                LabValue(
                    name="Potassium",
                    value=4.2,
                    unit="mEq/L",
                ),
            ]
        )
        assert len(results.lab_values) == 3

    def test_lab_results_empty_list(self) -> None:
        """Test that empty lab_values list raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            LabResultsInput(lab_values=[])
        assert "lab_values" in str(exc_info.value)

    def test_lab_results_missing_lab_values(self) -> None:
        """Test that missing lab_values raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            LabResultsInput()
        assert "lab_values" in str(exc_info.value)

    def test_lab_results_max_values(self) -> None:
        """Test that max 50 lab values is allowed."""
        lab_values_list = [
            LabValue(
                name=f"Test_{i}",
                value=float(i),
                unit="unit",
            )
            for i in range(50)
        ]
        results = LabResultsInput(lab_values=lab_values_list)
        assert len(results.lab_values) == 50

    def test_lab_results_exceeds_max_values(self) -> None:
        """Test that exceeding 50 lab values raises validation error."""
        lab_values_list = [
            LabValue(
                name=f"Test_{i}",
                value=float(i),
                unit="unit",
            )
            for i in range(51)
        ]
        with pytest.raises(ValidationError) as exc_info:
            LabResultsInput(lab_values=lab_values_list)
        assert "lab_values" in str(exc_info.value)

    def test_lab_results_invalid_item(self) -> None:
        """Test that invalid item in list raises validation error."""
        with pytest.raises(ValidationError):
            LabResultsInput(lab_values=[{"name": "Test"}])


class TestSeverityLevel:
    """Test SeverityLevel enum."""

    def test_severity_normal(self) -> None:
        """Test NORMAL severity level."""
        assert SeverityLevel.NORMAL == "normal"

    def test_severity_borderline(self) -> None:
        """Test BORDERLINE severity level."""
        assert SeverityLevel.BORDERLINE == "borderline"

    def test_severity_abnormal(self) -> None:
        """Test ABNORMAL severity level."""
        assert SeverityLevel.ABNORMAL == "abnormal"

    def test_severity_critical(self) -> None:
        """Test CRITICAL severity level."""
        assert SeverityLevel.CRITICAL == "critical"

    def test_severity_all_values(self) -> None:
        """Test all severity levels can be enumerated."""
        levels = list(SeverityLevel)
        assert len(levels) == 4
        assert SeverityLevel.NORMAL in levels
        assert SeverityLevel.BORDERLINE in levels
        assert SeverityLevel.ABNORMAL in levels
        assert SeverityLevel.CRITICAL in levels


class TestInterpretedValue:
    """Test InterpretedValue schema."""

    def test_valid_interpreted_value_with_citation(self) -> None:
        """Test creating valid interpreted value with citation."""
        interpreted = InterpretedValue(
            name="Hemoglobin",
            value=14.5,
            unit="g/dL",
            severity=SeverityLevel.NORMAL,
            explanation="Your hemoglobin level is within normal range.",
            citation="https://www.mayoclinic.org/tests-procedures/complete-blood-count/about/pac-20384919",
        )
        assert interpreted.name == "Hemoglobin"
        assert interpreted.value == 14.5
        assert interpreted.unit == "g/dL"
        assert interpreted.severity == SeverityLevel.NORMAL
        assert interpreted.citation is not None

    def test_valid_interpreted_value_without_citation(self) -> None:
        """Test creating valid interpreted value without citation."""
        interpreted = InterpretedValue(
            name="Hemoglobin",
            value=14.5,
            unit="g/dL",
            severity=SeverityLevel.NORMAL,
            explanation="Your hemoglobin level is within normal range.",
        )
        assert interpreted.citation is None

    def test_interpreted_value_missing_name(self) -> None:
        """Test that missing name raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            InterpretedValue(
                value=14.5,
                unit="g/dL",
                severity=SeverityLevel.NORMAL,
                explanation="Test",
            )
        assert "name" in str(exc_info.value)

    def test_interpreted_value_missing_severity(self) -> None:
        """Test that missing severity raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            InterpretedValue(
                name="Hemoglobin",
                value=14.5,
                unit="g/dL",
                explanation="Test",
            )
        assert "severity" in str(exc_info.value)

    def test_interpreted_value_invalid_severity(self) -> None:
        """Test that invalid severity raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            InterpretedValue(
                name="Hemoglobin",
                value=14.5,
                unit="g/dL",
                severity="invalid",  # type: ignore
                explanation="Test",
            )
        assert "severity" in str(exc_info.value)

    def test_interpreted_value_all_severities(self) -> None:
        """Test creating interpreted values with all severity levels."""
        for severity in SeverityLevel:
            interpreted = InterpretedValue(
                name="Test",
                value=1.0,
                unit="unit",
                severity=severity,
                explanation="Test explanation",
            )
            assert interpreted.severity == severity


class TestInterpretationResponse:
    """Test InterpretationResponse schema."""

    def test_valid_interpretation_response_single_result(self) -> None:
        """Test creating valid interpretation response with single result."""
        response = InterpretationResponse(
            results=[
                InterpretedValue(
                    name="Hemoglobin",
                    value=14.5,
                    unit="g/dL",
                    severity=SeverityLevel.NORMAL,
                    explanation="Normal level",
                )
            ],
            disclaimer="Always consult a doctor.",
        )
        assert len(response.results) == 1
        assert response.disclaimer == "Always consult a doctor."

    def test_valid_interpretation_response_multiple_results(self) -> None:
        """Test creating valid interpretation response with multiple results."""
        response = InterpretationResponse(
            results=[
                InterpretedValue(
                    name="Hemoglobin",
                    value=14.5,
                    unit="g/dL",
                    severity=SeverityLevel.NORMAL,
                    explanation="Normal level",
                ),
                InterpretedValue(
                    name="Glucose",
                    value=95.0,
                    unit="mg/dL",
                    severity=SeverityLevel.NORMAL,
                    explanation="Normal level",
                ),
            ],
            disclaimer="Always consult a doctor.",
            summary="Your results are normal.",
        )
        assert len(response.results) == 2
        assert response.summary == "Your results are normal."

    def test_interpretation_response_missing_results(self) -> None:
        """Test that missing results raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            InterpretationResponse(
                disclaimer="Always consult a doctor.",
            )
        assert "results" in str(exc_info.value)

    def test_interpretation_response_missing_disclaimer(self) -> None:
        """Test that missing disclaimer raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            InterpretationResponse(
                results=[
                    InterpretedValue(
                        name="Test",
                        value=1.0,
                        unit="unit",
                        severity=SeverityLevel.NORMAL,
                        explanation="Test",
                    )
                ],
            )
        assert "disclaimer" in str(exc_info.value)

    def test_interpretation_response_empty_results(self) -> None:
        """Test that empty results list is allowed."""
        response = InterpretationResponse(
            results=[],
            disclaimer="Always consult a doctor.",
        )
        assert len(response.results) == 0

    def test_interpretation_response_optional_summary(self) -> None:
        """Test that summary is optional."""
        response = InterpretationResponse(
            results=[],
            disclaimer="Always consult a doctor.",
            summary=None,
        )
        assert response.summary is None
