"""
Domain exceptions for Schedule DND application.

This module defines the exception hierarchy for domain-level errors.
Author: DmitrTRC
"""

from typing import Any, Optional


class ScheduleDNDError(Exception):
    """Base exception for all Schedule DND errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        """
        Initialize exception.

        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error details
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return string representation of exception."""
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


# ═══════════════════════════════════════════════════════════
# Validation Errors
# ═══════════════════════════════════════════════════════════


class ValidationError(ScheduleDNDError):
    """Raised when data validation fails."""

    def __init__(
        self, message: str, field: Optional[str] = None, value: Any = None
    ) -> None:
        """
        Initialize validation error.

        Args:
            message: Error message
            field: Name of the field that failed validation
            value: The invalid value
        """
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)
        super().__init__(message, details)
        self.field = field
        self.value = value


class DateValidationError(ValidationError):
    """Raised when date validation fails."""

    pass


class DutyTypeValidationError(ValidationError):
    """Raised when duty type validation fails."""

    pass


class MonthValidationError(ValidationError):
    """Raised when month validation fails."""

    pass


class YearValidationError(ValidationError):
    """Raised when year validation fails."""

    pass


class TimeValidationError(ValidationError):
    """Raised when time validation fails."""

    pass


# ═══════════════════════════════════════════════════════════
# Business Logic Errors
# ═══════════════════════════════════════════════════════════


class BusinessRuleViolation(ScheduleDNDError):
    """Raised when a business rule is violated."""

    pass


class DuplicateShiftError(BusinessRuleViolation):
    """Raised when attempting to create a duplicate shift."""

    def __init__(
        self, unit_name: str, date: str, existing_duty_type: Optional[str] = None
    ) -> None:
        """
        Initialize duplicate shift error.

        Args:
            unit_name: Name of the unit
            date: Date of the duplicate shift
            existing_duty_type: Type of the existing shift
        """
        message = f"Shift already exists for {unit_name} on {date}"
        if existing_duty_type:
            message += f" (type: {existing_duty_type})"
        super().__init__(message, {"unit": unit_name, "date": date})
        self.unit_name = unit_name
        self.date = date


class ShiftLimitExceeded(BusinessRuleViolation):
    """Raised when shift limit is exceeded for a unit."""

    def __init__(self, unit_name: str, limit: int, current: int) -> None:
        """
        Initialize shift limit error.

        Args:
            unit_name: Name of the unit
            limit: Maximum allowed shifts
            current: Current number of shifts
        """
        message = f"Shift limit exceeded for {unit_name}: {current}/{limit}"
        super().__init__(
            message, {"unit": unit_name, "limit": limit, "current": current}
        )
        self.unit_name = unit_name
        self.limit = limit
        self.current = current


class InvalidSchedulePeriod(BusinessRuleViolation):
    """Raised when schedule period is invalid."""

    pass


# ═══════════════════════════════════════════════════════════
# Data Errors
# ═══════════════════════════════════════════════════════════


class DataError(ScheduleDNDError):
    """Base class for data-related errors."""

    pass


class ScheduleNotFoundError(DataError):
    """Raised when schedule is not found."""

    def __init__(self, identifier: str) -> None:
        """
        Initialize schedule not found error.

        Args:
            identifier: Schedule identifier (e.g., filename, ID)
        """
        message = f"Schedule not found: {identifier}"
        super().__init__(message, {"identifier": identifier})
        self.identifier = identifier


class UnitNotFoundError(DataError):
    """Raised when unit is not found."""

    def __init__(self, unit_name: str) -> None:
        """
        Initialize unit not found error.

        Args:
            unit_name: Name of the unit
        """
        message = f"Unit not found: {unit_name}"
        super().__init__(message, {"unit": unit_name})
        self.unit_name = unit_name


class DataIntegrityError(DataError):
    """Raised when data integrity is compromised."""

    pass


class SerializationError(DataError):
    """Raised when data serialization/deserialization fails."""

    def __init__(self, format_type: str, reason: str) -> None:
        """
        Initialize serialization error.

        Args:
            format_type: Type of format (JSON, Excel, etc.)
            reason: Reason for failure
        """
        message = f"Failed to serialize/deserialize {format_type}: {reason}"
        super().__init__(message, {"format": format_type, "reason": reason})
        self.format_type = format_type
        self.reason = reason


# ═══════════════════════════════════════════════════════════
# File System Errors
# ═══════════════════════════════════════════════════════════


class FileSystemError(ScheduleDNDError):
    """Base class for file system errors."""

    pass


class FileNotFoundError(FileSystemError):
    """Raised when file is not found."""

    def __init__(self, filepath: str) -> None:
        """
        Initialize file not found error.

        Args:
            filepath: Path to the file
        """
        message = f"File not found: {filepath}"
        super().__init__(message, {"path": filepath})
        self.filepath = filepath


class FilePermissionError(FileSystemError):
    """Raised when file permission is denied."""

    def __init__(self, filepath: str, operation: str) -> None:
        """
        Initialize file permission error.

        Args:
            filepath: Path to the file
            operation: Operation that was attempted (read, write, etc.)
        """
        message = f"Permission denied for {operation} operation: {filepath}"
        super().__init__(message, {"path": filepath, "operation": operation})
        self.filepath = filepath
        self.operation = operation


class FileAlreadyExistsError(FileSystemError):
    """Raised when file already exists and overwrite is not allowed."""

    def __init__(self, filepath: str) -> None:
        """
        Initialize file already exists error.

        Args:
            filepath: Path to the file
        """
        message = f"File already exists: {filepath}"
        super().__init__(message, {"path": filepath})
        self.filepath = filepath


# ═══════════════════════════════════════════════════════════
# Export Errors
# ═══════════════════════════════════════════════════════════


class ExportError(ScheduleDNDError):
    """Base class for export-related errors."""

    pass


class UnsupportedFormatError(ExportError):
    """Raised when export format is not supported."""

    def __init__(self, format_name: str, supported_formats: list[str]) -> None:
        """
        Initialize unsupported format error.

        Args:
            format_name: Name of the unsupported format
            supported_formats: List of supported formats
        """
        supported = ", ".join(supported_formats)
        message = f"Unsupported export format: {format_name}. Supported: {supported}"
        super().__init__(
            message, {"format": format_name, "supported": supported_formats}
        )
        self.format_name = format_name
        self.supported_formats = supported_formats


class ExportFailedError(ExportError):
    """Raised when export operation fails."""

    def __init__(self, format_type: str, reason: str) -> None:
        """
        Initialize export failed error.

        Args:
            format_type: Type of format being exported
            reason: Reason for failure
        """
        message = f"Failed to export to {format_type}: {reason}"
        super().__init__(message, {"format": format_type, "reason": reason})
        self.format_type = format_type
        self.reason = reason


# ═══════════════════════════════════════════════════════════
# Configuration Errors
# ═══════════════════════════════════════════════════════════


class ConfigurationError(ScheduleDNDError):
    """Raised when configuration is invalid or missing."""

    pass


class MissingConfigurationError(ConfigurationError):
    """Raised when required configuration is missing."""

    def __init__(self, config_key: str) -> None:
        """
        Initialize missing configuration error.

        Args:
            config_key: Key of the missing configuration
        """
        message = f"Missing required configuration: {config_key}"
        super().__init__(message, {"key": config_key})
        self.config_key = config_key


class InvalidConfigurationError(ConfigurationError):
    """Raised when configuration value is invalid."""

    def __init__(self, config_key: str, value: Any, reason: str) -> None:
        """
        Initialize invalid configuration error.

        Args:
            config_key: Key of the configuration
            value: Invalid value
            reason: Reason why value is invalid
        """
        message = f"Invalid configuration for {config_key}: {reason}"
        super().__init__(
            message, {"key": config_key, "value": str(value), "reason": reason}
        )
        self.config_key = config_key
        self.value = value
        self.reason = reason
