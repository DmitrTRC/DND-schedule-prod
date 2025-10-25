"""
Extended comprehensive tests for validators module.

This file contains additional tests to achieve 90%+ coverage of validators.py
Author: DmitrTRC
"""

from datetime import datetime

import pytest

from schedule_dnd.domain.enums import DutyType, Month
from schedule_dnd.domain.exceptions import (
    DateValidationError,
    DutyTypeValidationError,
    MonthValidationError,
    TimeValidationError,
    UnitNotFoundError,
    YearValidationError,
)
from schedule_dnd.domain.validators import (
    format_date,
    get_month_days,
    is_date_in_future,
    parse_date,
    validate_date_format,
    validate_date_in_month,
    validate_date_string,
    validate_day,
    validate_duty_type,
    validate_month_name,
    validate_month_number,
    validate_schedule_period,
    validate_time_range,
    validate_unit_name,
    validate_year,
)


class TestValidateDay:
    """Tests for validate_day function."""

    def test_valid_day(self):
        """Test validation passes for valid day."""
        validate_day(15, 10, 2025)  # Should not raise

    def test_day_too_low(self):
        """Test validation fails for day < 1."""
        with pytest.raises(DateValidationError, match="Day must be between"):
            validate_day(0, 10, 2025)

    def test_day_too_high(self):
        """Test validation fails for day > 31."""
        with pytest.raises(DateValidationError, match="Day must be between"):
            validate_day(32, 10, 2025)

    def test_day_invalid_for_month(self):
        """Test validation fails for day not valid in month."""
        with pytest.raises(DateValidationError, match="This month has only"):
            validate_day(31, 2, 2025)  # February doesn't have 31 days

    def test_leap_year_february(self):
        """Test February 29 valid in leap year."""
        validate_day(29, 2, 2024)  # 2024 is leap year

    def test_non_leap_year_february(self):
        """Test February 29 invalid in non-leap year."""
        with pytest.raises(DateValidationError):
            validate_day(29, 2, 2025)  # 2025 is not leap year


class TestValidateMonthNumber:
    """Tests for validate_month_number function."""

    def test_valid_month(self):
        """Test validation passes for valid month."""
        for month in range(1, 13):
            validate_month_number(month)  # Should not raise

    def test_month_too_low(self):
        """Test validation fails for month < 1."""
        with pytest.raises(MonthValidationError):
            validate_month_number(0)

    def test_month_too_high(self):
        """Test validation fails for month > 12."""
        with pytest.raises(MonthValidationError):
            validate_month_number(13)


class TestValidateYear:
    """Tests for validate_year function."""

    def test_current_year(self):
        """Test validation passes for current year."""
        current_year = datetime.now().year
        validate_year(current_year)

    def test_future_year(self):
        """Test validation passes for future year."""
        current_year = datetime.now().year
        validate_year(current_year + 1)

    def test_past_year_not_allowed(self):
        """Test validation fails for past year when not allowed."""
        current_year = datetime.now().year
        with pytest.raises(YearValidationError):
            validate_year(current_year - 1, allow_past=False)

    def test_past_year_allowed(self):
        """Test validation passes for past year when allowed."""
        current_year = datetime.now().year
        validate_year(current_year - 1, allow_past=True)

    def test_year_too_far_future(self):
        """Test validation fails for year too far in future."""
        current_year = datetime.now().year
        with pytest.raises(YearValidationError):
            validate_year(current_year + 100)

    def test_year_too_far_past(self):
        """Test validation fails for year too far in past."""
        with pytest.raises(YearValidationError):
            validate_year(2000, allow_past=True)


class TestValidateDateString:
    """Tests for validate_date_string function."""

    def test_valid_future_date(self):
        """Test validation passes for valid future date."""
        future_date = "01.01.2030"
        result = validate_date_string(future_date)
        assert isinstance(result, datetime)
        assert result.year == 2030

    def test_valid_past_date_allowed(self):
        """Test validation passes for past date when allowed."""
        past_date = "01.01.2020"
        result = validate_date_string(past_date, allow_past=True)
        assert result.year == 2020

    def test_past_date_not_allowed(self):
        """Test validation fails for past date when not allowed."""
        past_date = "01.01.2020"
        with pytest.raises(DateValidationError, match="is in the past"):
            validate_date_string(past_date, allow_past=False)

    def test_invalid_format(self):
        """Test validation fails for invalid date format."""
        with pytest.raises(DateValidationError, match="Invalid date format"):
            validate_date_string("2025-10-25")  # Wrong format

    def test_invalid_date_values(self):
        """Test validation fails for invalid date values."""
        with pytest.raises(DateValidationError):
            validate_date_string("32.13.2025")


class TestValidateDateInMonth:
    """Tests for validate_date_in_month function."""

    def test_date_in_correct_month(self):
        """Test validation passes when date is in correct month."""
        validate_date_in_month("15.10.2025", 10, 2025)

    def test_date_in_wrong_month(self):
        """Test validation fails when date is in wrong month."""
        with pytest.raises(DateValidationError, match="is not in"):
            validate_date_in_month("15.11.2025", 10, 2025)

    def test_date_in_wrong_year(self):
        """Test validation fails when date is in wrong year."""
        with pytest.raises(DateValidationError, match="is not in"):
            validate_date_in_month("15.10.2024", 10, 2025)


class TestValidateDutyType:
    """Tests for validate_duty_type function."""

    def test_valid_duty_type_pdn(self):
        """Test validation passes for valid PDN duty type."""
        result = validate_duty_type("ПДН")
        assert result == DutyType.PDN

    def test_valid_duty_type_ppsp(self):
        """Test validation passes for valid PPSP duty type."""
        result = validate_duty_type("ППСП")
        assert result == DutyType.PPSP

    def test_valid_duty_type_uup(self):
        """Test validation passes for valid UUP duty type."""
        result = validate_duty_type("УУП")
        assert result == DutyType.UUP

    def test_invalid_duty_type(self):
        """Test validation fails for invalid duty type."""
        with pytest.raises(DutyTypeValidationError, match="Invalid duty type"):
            validate_duty_type("INVALID")


class TestValidateTimeRange:
    """Tests for validate_time_range function."""

    def test_valid_time_range(self):
        """Test validation passes for valid time range."""
        start, end = validate_time_range("09:00-18:00")
        assert start.hour == 9
        assert end.hour == 18

    def test_time_range_with_spaces(self):
        """Test validation handles spaces correctly."""
        start, end = validate_time_range(" 09:00 - 18:00 ")
        assert start.hour == 9
        assert end.hour == 18

    def test_invalid_format_no_dash(self):
        """Test validation fails without dash separator."""
        with pytest.raises(TimeValidationError, match="Invalid time range format"):
            validate_time_range("09:00 18:00")

    def test_invalid_time_format(self):
        """Test validation fails for invalid time format."""
        with pytest.raises(TimeValidationError, match="Invalid time format"):
            validate_time_range("25:00-26:00")

    def test_start_after_end(self):
        """Test validation fails when start time is after end time."""
        with pytest.raises(TimeValidationError, match="Start time must be before"):
            validate_time_range("18:00-09:00")

    def test_start_equals_end(self):
        """Test validation fails when start equals end."""
        with pytest.raises(TimeValidationError, match="Start time must be before"):
            validate_time_range("09:00-09:00")


class TestValidateUnitName:
    """Tests for validate_unit_name function."""

    def test_valid_unit_name(self):
        """Test validation passes for valid unit name from UNITS."""
        # Assuming first unit from UNITS is valid
        from schedule_dnd.domain.constants import UNITS

        if UNITS:
            validate_unit_name(UNITS[0])  # Should not raise

    def test_invalid_unit_name(self):
        """Test validation fails for invalid unit name."""
        with pytest.raises(UnitNotFoundError):
            validate_unit_name("Несуществующее подразделение")


class TestValidateMonthName:
    """Tests for validate_month_name function."""

    def test_valid_month_names(self):
        """Test validation passes for all valid Russian month names."""
        months = [
            ("январь", Month.JANUARY),
            ("февраль", Month.FEBRUARY),
            ("октябрь", Month.OCTOBER),
            ("декабрь", Month.DECEMBER),
        ]

        for name, expected in months:
            result = validate_month_name(name)
            assert result == expected

    def test_invalid_month_name(self):
        """Test validation fails for invalid month name."""
        with pytest.raises(MonthValidationError, match="Invalid month"):
            validate_month_name("InvalidMonth")


class TestValidateSchedulePeriod:
    """Tests for validate_schedule_period function."""

    def test_valid_current_period(self):
        """Test validation passes for current month/year."""
        current_date = datetime.now()
        validate_schedule_period(current_date.month, current_date.year)

    def test_valid_future_period(self):
        """Test validation passes for future period."""
        current_date = datetime.now()
        future_year = current_date.year + 1
        validate_schedule_period(1, future_year)

    def test_past_period_fails(self):
        """Test validation fails for past period."""
        current_date = datetime.now()

        # Calculate a definitely past period
        if current_date.month == 1:
            past_month = 12
            past_year = current_date.year - 1
        else:
            past_month = current_date.month - 1
            past_year = current_date.year

        with pytest.raises(DateValidationError, match="is in the past"):
            validate_schedule_period(past_month, past_year)


class TestIsDateInFuture:
    """Tests for is_date_in_future function."""

    def test_future_date(self):
        """Test returns True for future date."""
        assert is_date_in_future("01.01.2030") is True

    def test_past_date(self):
        """Test returns False for past date."""
        assert is_date_in_future("01.01.2020") is False

    def test_invalid_format(self):
        """Test returns False for invalid date format."""
        assert is_date_in_future("invalid") is False


class TestGetMonthDays:
    """Tests for get_month_days function."""

    def test_january_days(self):
        """Test returns 31 days for January."""
        assert get_month_days(1, 2025) == 31

    def test_february_non_leap(self):
        """Test returns 28 days for February in non-leap year."""
        assert get_month_days(2, 2025) == 28

    def test_february_leap(self):
        """Test returns 29 days for February in leap year."""
        assert get_month_days(2, 2024) == 29

    def test_april_days(self):
        """Test returns 30 days for April."""
        assert get_month_days(4, 2025) == 30


class TestFormatDate:
    """Tests for format_date function."""

    def test_format_valid_date(self):
        """Test formats date correctly."""
        result = format_date(15, 10, 2025)
        assert result == "15.10.2025"

    def test_format_single_digit(self):
        """Test formats single digits with leading zeros."""
        result = format_date(5, 3, 2025)
        assert result == "05.03.2025"

    def test_format_invalid_day(self):
        """Test raises error for invalid day."""
        with pytest.raises(DateValidationError):
            format_date(32, 10, 2025)

    def test_format_invalid_month(self):
        """Test raises error for invalid month."""
        with pytest.raises(MonthValidationError):
            format_date(15, 13, 2025)


class TestParseDate:
    """Tests for parse_date function."""

    def test_parse_valid_date(self):
        """Test parses date string correctly."""
        day, month, year = parse_date("15.10.2025")
        assert day == 15
        assert month == 10
        assert year == 2025

    def test_parse_invalid_format(self):
        """Test raises error for invalid format."""
        with pytest.raises(DateValidationError):
            parse_date("2025-10-15")

    def test_parse_invalid_date(self):
        """Test raises error for invalid date values."""
        with pytest.raises(DateValidationError):
            parse_date("32.13.2025")


class TestValidateDateFormat:
    """Tests for validate_date_format function."""

    def test_valid_format(self):
        """Test validation passes for correct format."""
        validate_date_format("15.10.2025")  # Should not raise

    def test_invalid_format_dashes(self):
        """Test validation fails for wrong separator."""
        with pytest.raises(DateValidationError, match="Invalid date format"):
            validate_date_format("15-10-2025")

    def test_invalid_format_slashes(self):
        """Test validation fails for slashes."""
        with pytest.raises(DateValidationError, match="Invalid date format"):
            validate_date_format("15/10/2025")

    def test_invalid_format_wrong_order(self):
        """Test validation fails for wrong component order."""
        with pytest.raises(DateValidationError, match="Invalid date format"):
            validate_date_format("2025.10.15")


class TestValidatorsIntegration:
    """Integration tests combining multiple validators."""

    def test_complete_date_validation_chain(self):
        """Test complete validation chain for a date."""
        # Validate components
        day, month, year = 15, 10, 2025
        validate_day(day, month, year)
        validate_month_number(month)
        validate_year(year, allow_past=False)

        # Format and parse
        date_str = format_date(day, month, year)
        assert date_str == "15.10.2025"

        parsed_day, parsed_month, parsed_year = parse_date(date_str)
        assert (parsed_day, parsed_month, parsed_year) == (day, month, year)

    def test_validate_shift_data(self):
        """Test validation of complete shift data."""
        # Validate all shift components
        date_str = "15.10.2025"
        validate_date_format(date_str)
        validate_date_in_month(date_str, 10, 2025)

        duty_type = validate_duty_type("ПДН")
        assert duty_type == DutyType.PDN

        start, end = validate_time_range("09:00-18:00")
        assert start.hour == 9
        assert end.hour == 18
