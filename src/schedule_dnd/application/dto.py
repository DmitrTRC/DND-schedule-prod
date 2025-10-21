"""
Data Transfer Objects for Schedule DND application.

DTOs are used to transfer data between different layers of the application.
They are simple, immutable data containers without business logic.

Author: DmitrTRC
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from schedule_dnd.domain.constants import UNITS
from schedule_dnd.domain.enums import DutyType, Month
from schedule_dnd.domain.validators import (
    validate_date_format,
    validate_date_in_month,
    validate_duty_type,
    validate_time_range,
)

# ═══════════════════════════════════════════════════════════
# Request DTOs
# ═══════════════════════════════════════════════════════════


class ShiftCreateDTO(BaseModel):
    """DTO for creating a new shift."""

    date: str = Field(..., description="Date in DD.MM.YYYY format")
    duty_type: DutyType = Field(..., description="Type of duty")
    time: str = Field(
        default="18:00-22:00",
        description="Time range in HH:MM-HH:MM format",
    )
    notes: str = Field(
        default="Получение инструкций в ОП. Время: 17:30",
        description="Additional notes for the shift",
    )

    @field_validator("date")
    @classmethod
    def validate_date_field(cls, value: str) -> str:
        """Validate date format."""
        validate_date_format(value)
        return value

    @field_validator("time")
    @classmethod
    def validate_time_field(cls, value: str) -> str:
        """Validate time format."""
        validate_time_range(value)
        return value


class UnitCreateDTO(BaseModel):
    """DTO for creating a unit with shifts."""

    unit_name: str = Field(..., description="Name of the DND unit")
    shifts: list[ShiftCreateDTO] = Field(
        default_factory=list, description="List of shifts for this unit"
    )

    @field_validator("unit_name")
    @classmethod
    def validate_unit_field(cls, value: str) -> str:
        """Validate unit name."""
        if value not in UNITS:
            raise ValueError(f"Invalid unit name: {value}")
        return value


class ScheduleCreateDTO(BaseModel):
    """DTO for creating a new schedule."""

    month: Month = Field(..., description="Month of the schedule")
    year: int = Field(..., description="Year of the schedule", ge=2020, le=2100)
    units: list[UnitCreateDTO] = Field(..., description="List of units with shifts")

    class Config:
        """Pydantic configuration."""

        use_enum_values = False


class ShiftUpdateDTO(BaseModel):
    """DTO for updating an existing shift."""

    date: Optional[str] = Field(None, description="New date in DD.MM.YYYY format")
    duty_type: Optional[DutyType] = Field(None, description="New type of duty")
    time: Optional[str] = Field(None, description="New time range")
    notes: Optional[str] = Field(None, description="New notes")

    @field_validator("date")
    @classmethod
    def validate_date_field(cls, value: Optional[str]) -> Optional[str]:
        """Validate date format if provided."""
        if value is not None:
            validate_date_format(value)
        return value

    @field_validator("time")
    @classmethod
    def validate_time_field(cls, value: Optional[str]) -> Optional[str]:
        """Validate time format if provided."""
        if value is not None:
            validate_time_range(value)
        return value


# ═══════════════════════════════════════════════════════════
# Response DTOs
# ═══════════════════════════════════════════════════════════


class ShiftResponseDTO(BaseModel):
    """DTO for shift data in responses."""

    date: str
    duty_type: DutyType
    time: str
    notes: str

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        from_attributes = True


class UnitResponseDTO(BaseModel):
    """DTO for unit data in responses."""

    id: int
    unit_name: str
    shifts: list[ShiftResponseDTO]

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class ScheduleMetadataDTO(BaseModel):
    """DTO for schedule metadata."""

    document_type: str = "patrol_schedule"
    month: str
    year: int
    created_at: datetime
    created_by: str = "manual_input"
    source: Optional[str] = None
    signatory: Optional[str] = None
    note: Optional[str] = None

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class ScheduleResponseDTO(BaseModel):
    """DTO for complete schedule data in responses."""

    metadata: ScheduleMetadataDTO
    schedule: list[UnitResponseDTO]

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class ScheduleListItemDTO(BaseModel):
    """DTO for schedule list item (summary)."""

    filename: str
    month: str
    year: int
    created_at: datetime
    unit_count: int
    total_shifts: int

    class Config:
        """Pydantic configuration."""

        from_attributes = True


# ═══════════════════════════════════════════════════════════
# Export DTOs
# ═══════════════════════════════════════════════════════════


class ExportRequestDTO(BaseModel):
    """DTO for export request."""

    schedule_id: Optional[str] = Field(
        None, description="ID or filename of the schedule to export"
    )
    format: str = Field(..., description="Export format (json, excel, csv, etc.)")
    output_path: Optional[str] = Field(
        None, description="Custom output path (optional)"
    )


class ExportResultDTO(BaseModel):
    """DTO for export result."""

    success: bool
    format: str
    output_path: str
    error: Optional[str] = None
    file_size: Optional[int] = None

    class Config:
        """Pydantic configuration."""

        from_attributes = True


# ═══════════════════════════════════════════════════════════
# Validation DTOs
# ═══════════════════════════════════════════════════════════


class ValidationResultDTO(BaseModel):
    """DTO for validation result."""

    is_valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class ShiftValidationDTO(BaseModel):
    """DTO for shift validation request."""

    date: str
    duty_type: str
    month: int
    year: int
    unit_name: str

    @field_validator("date")
    @classmethod
    def validate_date_field(cls, value: str) -> str:
        """Validate date format."""
        validate_date_format(value)
        return value

    @field_validator("duty_type")
    @classmethod
    def validate_duty_type_field(cls, value: str) -> str:
        """Validate duty type."""
        validate_duty_type(value)
        return value


# ═══════════════════════════════════════════════════════════
# Statistics DTOs
# ═══════════════════════════════════════════════════════════


class UnitStatisticsDTO(BaseModel):
    """DTO for unit statistics."""

    unit_name: str
    total_shifts: int
    shifts_by_type: dict[str, int]
    avg_shifts_per_week: float

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class ScheduleStatisticsDTO(BaseModel):
    """DTO for overall schedule statistics."""

    month: str
    year: int
    total_units: int
    total_shifts: int
    shifts_by_type: dict[str, int]
    units: list[UnitStatisticsDTO]

    class Config:
        """Pydantic configuration."""

        from_attributes = True
