"""
Domain models for Schedule DND application.

This module defines the core business entities using Pydantic models.
Author: DmitrTRC
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from schedule_dnd.domain.constants import (
    DEFAULT_SHIFT_NOTE,
    DEFAULT_SHIFT_TIME,
    MAX_SHIFTS_PER_UNIT,
    UNITS,
)
from schedule_dnd.domain.enums import DutyType, Month
from schedule_dnd.domain.exceptions import (
    BusinessRuleViolation,
    DuplicateShiftError,
    ShiftLimitExceeded,
    UnitNotFoundError,
)


class Shift(BaseModel):
    """
    Represents a single patrol shift.

    A shift is a scheduled patrol duty for a specific date and time,
    assigned to a DND unit with a specific duty type.

    Attributes:
        date: Date of the shift in DD.MM.YYYY format
        duty_type: Type of patrol duty (ПДН, ППСП, УУП)
        time: Time range for the shift (e.g., "18:00-22:00")
        notes: Optional notes about the shift

    Example:
        >>> shift = Shift(
        ...     date="07.10.2025",
        ...     duty_type=DutyType.UUP,
        ...     time="18:00-22:00"
        ... )
    """

    date: str = Field(
        ...,
        description="Date of the shift",
        examples=["07.10.2025", "15.10.2025"],
    )
    duty_type: DutyType = Field(
        ...,
        description="Type of patrol duty",
    )
    time: str = Field(
        default=DEFAULT_SHIFT_TIME,
        description="Time range for the shift",
        pattern=r"^\d{2}:\d{2}-\d{2}:\d{2}$",
    )
    notes: str = Field(
        default=DEFAULT_SHIFT_NOTE,
        description="Additional notes about the shift",
    )

    @field_validator("date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Validate date format is DD.MM.YYYY."""
        try:
            datetime.strptime(v, "%d.%m.%Y")
        except ValueError as e:
            raise ValueError(f"Invalid date format: {v}. Expected DD.MM.YYYY") from e
        return v

    @field_validator("time")
    @classmethod
    def validate_time_range(cls, v: str) -> str:
        """Validate time range format HH:MM-HH:MM."""
        parts = v.split("-")
        if len(parts) != 2:
            raise ValueError(f"Invalid time range format: {v}. Expected HH:MM-HH:MM")

        try:
            start_time = datetime.strptime(parts[0].strip(), "%H:%M")
            end_time = datetime.strptime(parts[1].strip(), "%H:%M")
        except ValueError as e:
            raise ValueError(f"Invalid time format in range: {v}") from e

        if start_time >= end_time:
            raise ValueError(f"Start time must be before end time: {v}")

        return v

    def get_date_object(self) -> datetime:
        """
        Convert date string to datetime object.

        Returns:
            datetime object representing the shift date
        """
        return datetime.strptime(self.date, "%d.%m.%Y")

    def is_past(self) -> bool:
        """
        Check if shift is in the past.

        Returns:
            True if shift date is before today
        """
        return self.get_date_object().date() < datetime.now().date()

    def get_day_of_week(self) -> str:
        """
        Get Russian name of the day of week.

        Returns:
            Day of week in Russian (e.g., 'Понедельник')
        """
        days = [
            "Понедельник",
            "Вторник",
            "Среда",
            "Четверг",
            "Пятница",
            "Суббота",
            "Воскресенье",
        ]
        return days[self.get_date_object().weekday()]

    def __str__(self) -> str:
        """String representation of shift."""
        return f"{self.date} - {self.duty_type.value} ({self.time})"

    model_config = ConfigDict(
        frozen=False,  # Allow updates
        use_enum_values=False,  # Keep enum objects
        validate_assignment=True,  # Validate on assignment
    )


class Unit(BaseModel):
    """
    Represents a DND unit with its scheduled shifts.

    A unit is one of the 8 Voluntary People's Squads that perform
    patrol duties according to the schedule.

    Attributes:
        id: Unique identifier for the unit (1-8)
        unit_name: Official name of the DND unit
        shifts: List of scheduled shifts for this unit

    Example:
        >>> unit = Unit(
        ...     id=1,
        ...     unit_name="ДНД «Всеволожский дозор»",
        ...     shifts=[]
        ... )
    """

    id: int = Field(
        ...,
        ge=1,
        le=8,
        description="Unique identifier for the unit",
    )
    unit_name: str = Field(
        ...,
        description="Official name of the DND unit",
    )
    shifts: list[Shift] = Field(
        default_factory=list,
        description="List of scheduled shifts",
    )

    @field_validator("unit_name")
    @classmethod
    def validate_unit_name(cls, v: str) -> str:
        """Validate that unit name is in the official list."""
        if v not in UNITS:
            valid_units = "\n".join(f"  - {u}" for u in UNITS)
            raise UnitNotFoundError(v)
        return v

    @model_validator(mode="after")
    def validate_shift_limit(self) -> "Unit":
        """Validate that unit doesn't exceed maximum shifts."""
        if len(self.shifts) > MAX_SHIFTS_PER_UNIT:
            raise ShiftLimitExceeded(
                unit_name=self.unit_name,
                limit=MAX_SHIFTS_PER_UNIT,
                current=len(self.shifts),
            )
        return self

    def add_shift(self, shift: Shift) -> None:
        """
        Add a shift to this unit.

        Args:
            shift: The shift to add

        Raises:
            DuplicateShiftError: If shift on this date already exists
            ShiftLimitExceeded: If adding would exceed maximum shifts
        """
        # Check for duplicates
        if self.has_shift_on_date(shift.date):
            existing = self.get_shift_by_date(shift.date)
            raise DuplicateShiftError(
                unit_name=self.unit_name,
                date=shift.date,
                existing_duty_type=existing.duty_type.value if existing else None,
            )

        # Check limit
        if len(self.shifts) >= MAX_SHIFTS_PER_UNIT:
            raise ShiftLimitExceeded(
                unit_name=self.unit_name,
                limit=MAX_SHIFTS_PER_UNIT,
                current=len(self.shifts),
            )

        self.shifts.append(shift)

    def remove_shift(self, date: str) -> bool:
        """
        Remove a shift by date.

        Args:
            date: Date of the shift to remove

        Returns:
            True if shift was removed, False if not found
        """
        for i, shift in enumerate(self.shifts):
            if shift.date == date:
                self.shifts.pop(i)
                return True
        return False

    def has_shift_on_date(self, date: str) -> bool:
        """
        Check if unit has a shift on given date.

        Args:
            date: Date to check

        Returns:
            True if shift exists on this date
        """
        return any(shift.date == date for shift in self.shifts)

    def get_shift_by_date(self, date: str) -> Optional[Shift]:
        """
        Get shift by date.

        Args:
            date: Date to search for

        Returns:
            Shift if found, None otherwise
        """
        for shift in self.shifts:
            if shift.date == date:
                return shift
        return None

    def get_shifts_sorted(self) -> list[Shift]:
        """
        Get shifts sorted by date.

        Returns:
            List of shifts sorted chronologically
        """
        return sorted(self.shifts, key=lambda s: s.get_date_object())

    def get_shift_count(self) -> int:
        """Get total number of shifts for this unit."""
        return len(self.shifts)

    def get_shifts_by_type(self) -> dict[str, int]:
        """
        Get count of shifts by duty type.

        Returns:
            Dictionary mapping duty type to count
        """
        result: dict[str, int] = {}
        for shift in self.shifts:
            duty_type_str = shift.duty_type.value
            result[duty_type_str] = result.get(duty_type_str, 0) + 1
        return result

    def __str__(self) -> str:
        """String representation of unit."""
        return f"{self.unit_name} ({self.get_shift_count()} shifts)"

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
    )


class ScheduleMetadata(BaseModel):
    """
    Metadata for a patrol schedule.

    Contains information about when and how the schedule was created.

    Attributes:
        document_type: Type of document (always "patrol_schedule")
        month: Month name in Russian
        year: Year of the schedule
        created_at: ISO timestamp of creation
        created_by: Who/what created the schedule
        version: Optional version identifier

    Example:
        >>> metadata = ScheduleMetadata(
        ...     month=Month.OCTOBER,
        ...     year=2025,
        ...     created_by="manual_input"
        ... )
    """

    document_type: str = Field(
        default="patrol_schedule",
        description="Type of document",
    )
    month: Month = Field(
        ...,
        description="Month of the schedule",
    )
    year: int = Field(
        ...,
        ge=2020,
        le=2100,
        description="Year of the schedule",
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp of creation",
    )
    created_by: str = Field(
        default="manual_input",
        description="Creator identifier",
    )
    source: Optional[str] = Field(
        default=None,
        description="Document source organization",
    )
    signatory: Optional[str] = Field(
        default=None,
        description="Person who signed the document",
    )
    note: Optional[str] = Field(
        default=None,
        description="Additional notes about the schedule",
    )
    version: Optional[str] = Field(
        default=None,
        description="Version identifier",
    )

    def get_month_number(self) -> int:
        """Get numeric month (1-12)."""
        return self.month.to_number()

    def get_period_string(self) -> str:
        """Get formatted period string (e.g., 'October 2025')."""
        return f"{self.month.value.capitalize()} {self.year}"

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
    )


class Schedule(BaseModel):
    """
    Complete patrol schedule for a month.

    Represents the full schedule for all DND units for a specific month.

    Attributes:
        metadata: Schedule metadata (month, year, etc.)
        units: List of units with their shifts

    Example:
        >>> schedule = Schedule(
        ...     metadata=ScheduleMetadata(month=Month.OCTOBER, year=2025),
        ...     units=[]
        ... )
    """

    metadata: ScheduleMetadata = Field(
        ...,
        description="Schedule metadata",
    )
    units: list[Unit] = Field(
        default_factory=list,
        description="List of units with shifts",
    )

    @model_validator(mode="after")
    def validate_units(self) -> "Schedule":
        """Validate that all units are unique and in valid range."""
        unit_ids = [unit.id for unit in self.units]
        unit_names = [unit.unit_name for unit in self.units]

        # Check for duplicate IDs
        if len(unit_ids) != len(set(unit_ids)):
            raise BusinessRuleViolation("Duplicate unit IDs found")

        # Check for duplicate names
        if len(unit_names) != len(set(unit_names)):
            raise BusinessRuleViolation("Duplicate unit names found")

        return self

    def add_unit(self, unit: Unit) -> None:
        """
        Add a unit to the schedule.

        Args:
            unit: Unit to add

        Raises:
            BusinessRuleViolation: If unit with this ID or name already exists
        """
        # Check for duplicates
        if self.get_unit_by_id(unit.id) is not None:
            raise BusinessRuleViolation(f"Unit with ID {unit.id} already exists")

        if self.get_unit_by_name(unit.unit_name) is not None:
            raise BusinessRuleViolation(
                f"Unit with name {unit.unit_name} already exists"
            )

        self.units.append(unit)

    def get_unit_by_id(self, unit_id: int) -> Optional[Unit]:
        """Get unit by ID."""
        for unit in self.units:
            if unit.id == unit_id:
                return unit
        return None

    def get_unit_by_name(self, unit_name: str) -> Optional[Unit]:
        """Get unit by name."""
        for unit in self.units:
            if unit.unit_name == unit_name:
                return unit
        return None

    def get_total_shifts(self) -> int:
        """Get total number of shifts across all units."""
        return sum(unit.get_shift_count() for unit in self.units)

    def get_units_with_shifts(self) -> list[Unit]:
        """Get only units that have at least one shift."""
        return [unit for unit in self.units if unit.get_shift_count() > 0]

    def get_shifts_by_type(self) -> dict[str, int]:
        """
        Get count of all shifts by duty type across all units.

        Returns:
            Dictionary mapping duty type to total count
        """
        result: dict[str, int] = {}
        for unit in self.units:
            for shift in unit.shifts:
                duty_type_str = shift.duty_type.value
                result[duty_type_str] = result.get(duty_type_str, 0) + 1
        return result

    def to_dict(self) -> dict[str, Any]:
        """
        Convert schedule to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the schedule
        """
        return {
            "metadata": {
                "document_type": self.metadata.document_type,
                "month": self.metadata.month.value,
                "year": self.metadata.year,
                "created_at": self.metadata.created_at.isoformat(),
                "created_by": self.metadata.created_by,
            },
            "schedule": [
                {
                    "id": unit.id,
                    "unit_name": unit.unit_name,
                    "shifts": [
                        {
                            "date": shift.date,
                            "duty_type": shift.duty_type.value,
                            "time": shift.time,
                            "notes": shift.notes,
                        }
                        for shift in unit.shifts
                    ],
                }
                for unit in self.units
            ],
        }

    def __str__(self) -> str:
        """String representation of schedule."""
        period = self.metadata.get_period_string()
        total = self.get_total_shifts()
        units_count = len(self.get_units_with_shifts())
        return f"Schedule for {period}: {total} shifts across {units_count} units"

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
    )
