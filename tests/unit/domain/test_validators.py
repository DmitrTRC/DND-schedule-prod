"""
Domain validation rules for Schedule DND application.

This module provides validation functions for business rules and constraints.
Author: DmitrTRC
"""

import calendar
from datetime import datetime
from typing import Optional

from schedule_dnd.domain.constants import (
    MAX_DAY,
    MAX_MONTH,
    MAX_YEAR_OFFSET,
    MIN_DAY,
    MIN_MONTH,
    MIN_YEAR_OFFSET,
    UNITS,
)
from schedule_dnd.domain.enums import DutyType, Month
from schedule_dnd.domain.exceptions import (
    DateValidationError,
    DutyTypeValidationError,
    MonthValidationError,
    TimeValidationError,
    UnitNotFoundError,
    YearValidationError,
)


def validate_day(day: int, month: int, year: int) -> None:
    """
    Validate day of month.

    Args:
        day: Day to validate (1-31)
        month: Month (1-12)
        year: Year

    Raises:
        DateValidationError: If day is invalid for given month/year
    """
    if not MIN_DAY <= day <= MAX_DAY:
        raise DateValidationError(
            f"Day must be between {MIN_DAY} and {MAX_DAY}",
            field="day",
            value=day,
        )

    # Check if day is valid for the specific month
    max_day_in_month = calendar.monthrange(year, month)[1]
    if day > max_day_in_month:
        raise DateValidationError(
            f"Day {day} is invalid for month {month}/{year}. "
            f"This month has only {max_day_in_month} days",
            field="day",
            value=day,
        )


def validate_month_number(month: int) -> None:
    """
    Validate month number.

    Args:
        month: Month number to validate (1-12)

    Raises:
        MonthValidationError: If month is invalid
    """
    if not MIN_MONTH <= month <= MAX_MONTH:
        raise MonthValidationError(
            f"Month must be between {MIN_MONTH} and {MAX_MONTH}",
            field="month",
            value=month,
        )


def validate_year(year: int, allow_past: bool = False) -> None:
    """
    Validate year.

    Args:
        year: Year to validate
        allow_past: Whether to allow years in the past

    Raises:
        YearValidationError: If year is invalid
    """
    current_year = datetime.now().year
    min_year = current_year if not allow_past else current_year - 10
    max_year = current_year + MAX_YEAR_OFFSET

    if year < min_year:
        raise YearValidationError(
            f"Year cannot be before {min_year}",
            field="year",
            value=year,
        )

    if year > max_year:
        raise YearValidationError(
            f"Year cannot be after {max_year}",
            field="year",
            value=year,
        )


def validate_date_string(date_str: str, allow_past: bool = False) -> datetime:
    """
    Validate date string in DD.MM.YYYY format.

    Args:
        date_str: Date string to validate
        allow_past: Whether to allow dates in the past

    Returns:
        datetime object if validation passes

    Raises:
        DateValidationError: If date format or value is invalid
    """
    try:
        date_obj = datetime.strptime(date_str, "%d.%m.%Y")
    except ValueError as e:
        raise DateValidationError(
            f"Invalid date format: {date_str}. Expected DD.MM.YYYY",
            field="date",
            value=date_str,
        ) from e

    # Check if date is in the past
    if not allow_past and date_obj.date() < datetime.now().date():
        raise DateValidationError(
            f"Date {date_str} is in the past",
            field="date",
            value=date_str,
        )

    return date_obj


def validate_date_in_month(date_str: str, month: int, year: int) -> None:
    """
    Validate that date is in the specified month and year.

    Args:
        date_str: Date string in DD.MM.YYYY format
        month: Expected month (1-12)
        year: Expected year

    Raises:
        DateValidationError: If date is not in the specified month/year
    """
    date_obj = validate_date_string(date_str, allow_past=True)

    if date_obj.month != month or date_obj.year != year:
        raise DateValidationError(
            f"Date {date_str} is not in {month}/{year}",
            field="date",
            value=date_str,
        )


def validate_duty_type(duty_type_str: str) -> DutyType:
    """
    Validate and convert duty type string.

    Args:
        duty_type_str: Duty type string to validate

    Returns:
        DutyType enum value

    Raises:
        DutyTypeValidationError: If duty type is invalid
    """
    try:
        return DutyType.from_string(duty_type_str)
    except ValueError as e:
        valid_types = ", ".join([dt.value for dt in DutyType])
        raise DutyTypeValidationError(
            f"Invalid duty type: {duty_type_str}. Valid types: {valid_types}",
            field="duty_type",
            value=duty_type_str,
        ) from e


def validate_time_range(time_range: str) -> tuple[datetime, datetime]:
    """
    Validate time range in HH:MM-HH:MM format.

    Args:
        time_range: Time range string to validate

    Returns:
        Tuple of (start_time, end_time) as datetime objects

    Raises:
        TimeValidationError: If time range format or values are invalid
    """
    parts = time_range.split("-")
    if len(parts) != 2:
        raise TimeValidationError(
            f"Invalid time range format: {time_range}. Expected HH:MM-HH:MM",
            field="time",
            value=time_range,
        )

    try:
        start_time = datetime.strptime(parts[0].strip(), "%H:%M")
        end_time = datetime.strptime(parts[1].strip(), "%H:%M")
    except ValueError as e:
        raise TimeValidationError(
            f"Invalid time format in range: {time_range}",
            field="time",
            value=time_range,
        ) from e

    if start_time >= end_time:
        raise TimeValidationError(
            f"Start time must be before end time: {time_range}",
            field="time",
            value=time_range,
        )

    return start_time, end_time


def validate_unit_name(unit_name: str) -> None:
    """
    Validate unit name.

    Args:
        unit_name: Unit name to validate

    Raises:
        UnitNotFoundError: If unit name is not in the official list
    """
    if unit_name not in UNITS:
        raise UnitNotFoundError(unit_name)


def validate_month_name(month_name: str) -> Month:
    """
    Validate and convert month name.

    Args:
        month_name: Month name in Russian

    Returns:
        Month enum value

    Raises:
        MonthValidationError: If month name is invalid
    """
    try:
        return Month.from_string(month_name)
    except ValueError as e:
        valid_months = ", ".join([m.value for m in Month])
        raise MonthValidationError(
            f"Invalid month: {month_name}. Valid months: {valid_months}",
            field="month",
            value=month_name,
        ) from e


def validate_schedule_period(month: int, year: int) -> None:
    """
    Validate schedule period (month and year combination).

    Args:
        month: Month number (1-12)
        year: Year

    Raises:
        DateValidationError: If period is invalid
    """
    validate_month_number(month)
    validate_year(year, allow_past=False)

    # Check if period is not too far in the past
    current_date = datetime.now()
    period_date = datetime(year, month, 1)

    # Allow current month and future months
    if period_date < datetime(current_date.year, current_date.month, 1):
        raise DateValidationError(
            f"Schedule period {month}/{year} is in the past",
            field="period",
            value=f"{month}/{year}",
        )


def is_date_in_future(date_str: str) -> bool:
    """
    Check if date is in the future.

    Args:
        date_str: Date string in DD.MM.YYYY format

    Returns:
        True if date is in the future, False otherwise
    """
    try:
        date_obj = datetime.strptime(date_str, "%d.%m.%Y")
        return date_obj.date() > datetime.now().date()
    except ValueError:
        return False


def get_month_days(month: int, year: int) -> int:
    """
    Get number of days in a month.

    Args:
        month: Month number (1-12)
        year: Year

    Returns:
        Number of days in the month
    """
    return calendar.monthrange(year, month)[1]


def format_date(day: int, month: int, year: int) -> str:
    """
    Format day, month, year into DD.MM.YYYY string.

    Args:
        day: Day (1-31)
        month: Month (1-12)
        year: Year

    Returns:
        Formatted date string

    Raises:
        DateValidationError: If date components are invalid
    """
    validate_day(day, month, year)
    validate_month_number(month)
    validate_year(year, allow_past=True)

    return f"{day:02d}.{month:02d}.{year}"


def parse_date(date_str: str) -> tuple[int, int, int]:
    """
    Parse date string into day, month, year.

    Args:
        date_str: Date string in DD.MM.YYYY format

    Returns:
        Tuple of (day, month, year)

    Raises:
        DateValidationError: If date format is invalid
    """
    date_obj = validate_date_string(date_str, allow_past=True)
    return date_obj.day, date_obj.month, date_obj.year
