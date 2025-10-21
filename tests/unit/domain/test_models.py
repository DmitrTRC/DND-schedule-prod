"""
Unit tests for domain models.

Author: DmitrTRC
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from schedule_dnd.domain.enums import DutyType, Month
from schedule_dnd.domain.exceptions import (
    BusinessRuleViolation,
    DuplicateShiftError,
    ShiftLimitExceeded,
    UnitNotFoundError,
)
from schedule_dnd.domain.models import Schedule, ScheduleMetadata, Shift, Unit


class TestShift:
    """Test cases for Shift model."""

    def test_create_valid_shift(self) -> None:
        """Test creating a valid shift."""
        shift = Shift(
            date="07.10.2025",
            duty_type=DutyType.UUP,
            time="18:00-22:00",
            notes="Test note",
        )

        assert shift.date == "07.10.2025"
        assert shift.duty_type == DutyType.UUP
        assert shift.time == "18:00-22:00"
        assert shift.notes == "Test note"

    def test_create_shift_with_defaults(self) -> None:
        """Test creating shift with default values."""
        shift = Shift(date="07.10.2025", duty_type=DutyType.PDN)

        assert shift.time == "18:00-22:00"
        assert "инструкций" in shift.notes

    def test_invalid_date_format(self) -> None:
        """Test that invalid date format raises error."""
        with pytest.raises(ValidationError):
            Shift(date="2025-10-07", duty_type=DutyType.UUP)  # Wrong format

    def test_invalid_time_format(self) -> None:
        """Test that invalid time format raises error."""
        with pytest.raises(ValidationError):
            Shift(
                date="07.10.2025",
                duty_type=DutyType.UUP,
                time="18:00",  # Missing end time
            )

    def test_time_range_validation(self) -> None:
        """Test that end time must be after start time."""
        with pytest.raises(ValidationError):
            Shift(
                date="07.10.2025",
                duty_type=DutyType.UUP,
                time="22:00-18:00",  # End before start
            )

    def test_get_date_object(self) -> None:
        """Test converting date string to datetime object."""
        shift = Shift(date="07.10.2025", duty_type=DutyType.UUP)

        date_obj = shift.get_date_object()
        assert date_obj.day == 7
        assert date_obj.month == 10
        assert date_obj.year == 2025

    def test_is_past(self) -> None:
        """Test checking if shift is in the past."""
        past_shift = Shift(date="01.01.2020", duty_type=DutyType.UUP)

        assert past_shift.is_past() is True

    def test_str_representation(self) -> None:
        """Test string representation of shift."""
        shift = Shift(date="07.10.2025", duty_type=DutyType.UUP, time="18:00-22:00")

        str_repr = str(shift)
        assert "07.10.2025" in str_repr
        assert "УУП" in str_repr
        assert "18:00-22:00" in str_repr


class TestUnit:
    """Test cases for Unit model."""

    def test_create_valid_unit(self) -> None:
        """Test creating a valid unit."""
        unit = Unit(id=1, unit_name="ДНД «Всеволожский дозор»", shifts=[])

        assert unit.id == 1
        assert unit.unit_name == "ДНД «Всеволожский дозор»"
        assert len(unit.shifts) == 0

    def test_invalid_unit_name(self) -> None:
        """Test that invalid unit name raises error."""
        with pytest.raises(UnitNotFoundError):
            Unit(id=1, unit_name="Invalid Unit Name", shifts=[])

    def test_invalid_unit_id(self) -> None:
        """Test that unit ID must be 1-8."""
        with pytest.raises(ValidationError):
            Unit(id=0, unit_name="ДНД «Всеволожский дозор»")  # Invalid

        with pytest.raises(ValidationError):
            Unit(id=9, unit_name="ДНД «Всеволожский дозор»")  # Invalid

    def test_add_shift(self) -> None:
        """Test adding a shift to unit."""
        unit = Unit(id=1, unit_name="ДНД «Всеволожский дозор»")

        shift = Shift(date="07.10.2025", duty_type=DutyType.UUP)

        unit.add_shift(shift)
        assert len(unit.shifts) == 1
        assert unit.get_shift_count() == 1

    def test_add_duplicate_shift(self) -> None:
        """Test that adding duplicate shift raises error."""
        unit = Unit(id=1, unit_name="ДНД «Всеволожский дозор»")

        shift1 = Shift(date="07.10.2025", duty_type=DutyType.UUP)
        shift2 = Shift(date="07.10.2025", duty_type=DutyType.PDN)

        unit.add_shift(shift1)

        with pytest.raises(DuplicateShiftError):
            unit.add_shift(shift2)

    def test_has_shift_on_date(self) -> None:
        """Test checking if unit has shift on date."""
        unit = Unit(id=1, unit_name="ДНД «Всеволожский дозор»")

        shift = Shift(date="07.10.2025", duty_type=DutyType.UUP)
        unit.add_shift(shift)

        assert unit.has_shift_on_date("07.10.2025") is True
        assert unit.has_shift_on_date("08.10.2025") is False

    def test_get_shift_by_date(self) -> None:
        """Test getting shift by date."""
        unit = Unit(id=1, unit_name="ДНД «Всеволожский дозор»")

        shift = Shift(date="07.10.2025", duty_type=DutyType.UUP)
        unit.add_shift(shift)

        found = unit.get_shift_by_date("07.10.2025")
        assert found is not None
        assert found.date == "07.10.2025"

        not_found = unit.get_shift_by_date("08.10.2025")
        assert not_found is None

    def test_remove_shift(self) -> None:
        """Test removing a shift."""
        unit = Unit(id=1, unit_name="ДНД «Всеволожский дозор»")

        shift = Shift(date="07.10.2025", duty_type=DutyType.UUP)
        unit.add_shift(shift)

        assert unit.remove_shift("07.10.2025") is True
        assert len(unit.shifts) == 0

        assert unit.remove_shift("08.10.2025") is False

    def test_get_shifts_sorted(self) -> None:
        """Test getting shifts sorted by date."""
        unit = Unit(id=1, unit_name="ДНД «Всеволожский дозор»")

        # Add shifts in random order
        unit.add_shift(Shift(date="15.10.2025", duty_type=DutyType.UUP))
        unit.add_shift(Shift(date="07.10.2025", duty_type=DutyType.PDN))
        unit.add_shift(Shift(date="22.10.2025", duty_type=DutyType.PPSP))

        sorted_shifts = unit.get_shifts_sorted()

        assert sorted_shifts[0].date == "07.10.2025"
        assert sorted_shifts[1].date == "15.10.2025"
        assert sorted_shifts[2].date == "22.10.2025"

    def test_str_representation(self) -> None:
        """Test string representation of unit."""
        unit = Unit(id=1, unit_name="ДНД «Всеволожский дозор»")
        unit.add_shift(Shift(date="07.10.2025", duty_type=DutyType.UUP))

        str_repr = str(unit)
        assert "Всеволожский дозор" in str_repr
        assert "1 shifts" in str_repr


class TestScheduleMetadata:
    """Test cases for ScheduleMetadata model."""

    def test_create_valid_metadata(self) -> None:
        """Test creating valid metadata."""
        metadata = ScheduleMetadata(
            month=Month.OCTOBER, year=2025, created_by="test_user"
        )

        assert metadata.month == Month.OCTOBER
        assert metadata.year == 2025
        assert metadata.created_by == "test_user"
        assert metadata.document_type == "patrol_schedule"

    def test_get_month_number(self) -> None:
        """Test getting numeric month."""
        metadata = ScheduleMetadata(month=Month.OCTOBER, year=2025)

        assert metadata.get_month_number() == 10

    def test_get_period_string(self) -> None:
        """Test getting formatted period string."""
        metadata = ScheduleMetadata(month=Month.OCTOBER, year=2025)

        period = metadata.get_period_string()
        assert "октябрь" in period.lower()
        assert "2025" in period


class TestSchedule:
    """Test cases for Schedule model."""

    def test_create_empty_schedule(self) -> None:
        """Test creating empty schedule."""
        metadata = ScheduleMetadata(month=Month.OCTOBER, year=2025)

        schedule = Schedule(metadata=metadata, units=[])

        assert schedule.metadata.month == Month.OCTOBER
        assert len(schedule.units) == 0
        assert schedule.get_total_shifts() == 0

    def test_add_unit(self) -> None:
        """Test adding a unit to schedule."""
        metadata = ScheduleMetadata(month=Month.OCTOBER, year=2025)
        schedule = Schedule(metadata=metadata)

        unit = Unit(id=1, unit_name="ДНД «Всеволожский дозор»")

        schedule.add_unit(unit)
        assert len(schedule.units) == 1

    def test_add_duplicate_unit_by_id(self) -> None:
        """Test that adding duplicate unit by ID raises error."""
        metadata = ScheduleMetadata(month=Month.OCTOBER, year=2025)
        schedule = Schedule(metadata=metadata)

        unit1 = Unit(id=1, unit_name="ДНД «Всеволожский дозор»")
        unit2 = Unit(id=1, unit_name="ДНД «Заневское ГП»")

        schedule.add_unit(unit1)

        with pytest.raises(BusinessRuleViolation):
            schedule.add_unit(unit2)

    def test_get_unit_by_id(self) -> None:
        """Test getting unit by ID."""
        metadata = ScheduleMetadata(month=Month.OCTOBER, year=2025)
        schedule = Schedule(metadata=metadata)

        unit = Unit(id=1, unit_name="ДНД «Всеволожский дозор»")
        schedule.add_unit(unit)

        found = schedule.get_unit_by_id(1)
        assert found is not None
        assert found.id == 1

        not_found = schedule.get_unit_by_id(2)
        assert not_found is None

    def test_get_unit_by_name(self) -> None:
        """Test getting unit by name."""
        metadata = ScheduleMetadata(month=Month.OCTOBER, year=2025)
        schedule = Schedule(metadata=metadata)

        unit = Unit(id=1, unit_name="ДНД «Всеволожский дозор»")
        schedule.add_unit(unit)

        found = schedule.get_unit_by_name("ДНД «Всеволожский дозор»")
        assert found is not None

    def test_get_total_shifts(self) -> None:
        """Test getting total shifts count."""
        metadata = ScheduleMetadata(month=Month.OCTOBER, year=2025)
        schedule = Schedule(metadata=metadata)

        unit1 = Unit(id=1, unit_name="ДНД «Всеволожский дозор»")
        unit1.add_shift(Shift(date="07.10.2025", duty_type=DutyType.UUP))
        unit1.add_shift(Shift(date="15.10.2025", duty_type=DutyType.PDN))

        unit2 = Unit(id=2, unit_name="ДНД «Заневское ГП»")
        unit2.add_shift(Shift(date="08.10.2025", duty_type=DutyType.PPSP))

        schedule.add_unit(unit1)
        schedule.add_unit(unit2)

        assert schedule.get_total_shifts() == 3

    def test_get_units_with_shifts(self) -> None:
        """Test getting only units that have shifts."""
        metadata = ScheduleMetadata(month=Month.OCTOBER, year=2025)
        schedule = Schedule(metadata=metadata)

        unit1 = Unit(id=1, unit_name="ДНД «Всеволожский дозор»")
        unit1.add_shift(Shift(date="07.10.2025", duty_type=DutyType.UUP))

        unit2 = Unit(id=2, unit_name="ДНД «Заневское ГП»")  # No shifts

        schedule.add_unit(unit1)
        schedule.add_unit(unit2)

        units_with_shifts = schedule.get_units_with_shifts()
        assert len(units_with_shifts) == 1
        assert units_with_shifts[0].id == 1

    def test_to_dict(self) -> None:
        """Test converting schedule to dictionary."""
        metadata = ScheduleMetadata(month=Month.OCTOBER, year=2025)
        schedule = Schedule(metadata=metadata)

        unit = Unit(id=1, unit_name="ДНД «Всеволожский дозор»")
        unit.add_shift(Shift(date="07.10.2025", duty_type=DutyType.UUP))
        schedule.add_unit(unit)

        data = schedule.to_dict()

        assert data["metadata"]["month"] == "октябрь"
        assert data["metadata"]["year"] == 2025
        assert len(data["schedule"]) == 1
        assert len(data["schedule"][0]["shifts"]) == 1

    def test_str_representation(self) -> None:
        """Test string representation of schedule."""
        metadata = ScheduleMetadata(month=Month.OCTOBER, year=2025)
        schedule = Schedule(metadata=metadata)

        unit = Unit(id=1, unit_name="ДНД «Всеволожский дозор»")
        unit.add_shift(Shift(date="07.10.2025", duty_type=DutyType.UUP))
        schedule.add_unit(unit)

        str_repr = str(schedule)
        assert "октябрь" in str_repr.lower()
        assert "2025" in str_repr
        assert "1 shifts" in str_repr
