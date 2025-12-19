"""Pydantic schemas for lab results."""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class LabValue(BaseModel):
    """Single lab test value."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Hemoglobin",
                "value": 14.5,
                "unit": "g/dL",
                "reference_min": 13.5,
                "reference_max": 17.5,
            }
        }
    )

    name: str = Field(
        ...,
        description="Name of the lab test",
        examples=["Hemoglobin"],
        min_length=1,
        max_length=100,
    )
    value: float = Field(
        ...,
        description="Measured value",
    )
    unit: str = Field(
        ...,
        description="Unit of measurement",
        examples=["g/dL"],
        min_length=1,
        max_length=50,
    )
    reference_min: float | None = Field(
        None,
        description="Minimum reference range",
    )
    reference_max: float | None = Field(
        None,
        description="Maximum reference range",
    )


class LabResultsInput(BaseModel):
    """Input payload for lab interpretation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
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
        }
    )

    lab_values: list[LabValue] = Field(
        ...,
        description="List of lab values to interpret",
        min_length=1,
        max_length=50,
    )


class SeverityLevel(str, Enum):
    """Severity level for abnormal values."""

    NORMAL = "normal"
    BORDERLINE = "borderline"
    ABNORMAL = "abnormal"
    CRITICAL = "critical"


class InterpretedValue(BaseModel):
    """Single interpreted lab value."""

    name: str = Field(..., description="Name of the lab test")
    value: float = Field(..., description="Measured value")
    unit: str = Field(..., description="Unit of measurement")
    severity: SeverityLevel = Field(..., description="Severity classification")
    explanation: str = Field(..., description="Plain-language explanation")
    citation: str | None = Field(
        None,
        description="Citation to authoritative source",
    )


class InterpretationResponse(BaseModel):
    """Full interpretation response."""

    results: list[InterpretedValue] = Field(
        ...,
        description="List of interpreted lab values",
    )
    disclaimer: str = Field(
        ...,
        description="Medical disclaimer",
    )
    summary: str | None = Field(
        None,
        description="Overall summary of results",
    )
