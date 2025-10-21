"""
Domain enumerations for Schedule DND application.

This module defines all enum types used in the domain layer.
Author: DmitrTRC
"""

from enum import Enum


class DutyType(str, Enum):
    """Types of patrol duties."""

    PDN = "ПДН"  # Подразделение по делам несовершеннолетних
    PPSP = "ППСП"  # Патрульно-постовая служба полиции
    UUP = "УУП"  # Участковые уполномоченные полиции

    @classmethod
    def from_string(cls, value: str) -> "DutyType":
        """
        Create DutyType from string value.

        Args:
            value: String representation of duty type

        Returns:
            DutyType enum value

        Raises:
            ValueError: If value doesn't match any duty type
        """
        value_upper = value.upper().strip()
        for duty_type in cls:
            if duty_type.value == value_upper or duty_type.name == value_upper:
                return duty_type
        valid_types = ", ".join([dt.value for dt in cls])
        raise ValueError(f"Invalid duty type: {value}. Valid types: {valid_types}")

    def __str__(self) -> str:
        """Return string representation."""
        return self.value


class Month(str, Enum):
    """Russian month names with their numbers."""

    JANUARY = "январь"
    FEBRUARY = "февраль"
    MARCH = "март"
    APRIL = "апрель"
    MAY = "май"
    JUNE = "июнь"
    JULY = "июль"
    AUGUST = "август"
    SEPTEMBER = "сентябрь"
    OCTOBER = "октябрь"
    NOVEMBER = "ноябрь"
    DECEMBER = "декабрь"

    @classmethod
    def from_string(cls, value: str) -> "Month":
        """
        Create Month from string value.

        Args:
            value: String representation of month (Russian name)

        Returns:
            Month enum value

        Raises:
            ValueError: If value doesn't match any month
        """
        value_lower = value.lower().strip()
        for month in cls:
            if month.value == value_lower:
                return month
        valid_months = ", ".join([m.value for m in cls])
        raise ValueError(f"Invalid month: {value}. Valid months: {valid_months}")

    def to_number(self) -> int:
        """
        Convert month to its number (1-12).

        Returns:
            Month number (1 for January, 12 for December)
        """
        return list(Month).index(self) + 1

    def display_name(self) -> str:
        """Get capitalized display name."""
        return self.value.capitalize()

    @classmethod
    def from_russian_name(cls, name: str) -> "Month":
        """Alias for from_string for better clarity."""
        return cls.from_string(name)

    @classmethod
    def from_number(cls, number: int) -> "Month":
        """
        Create Month from number (1-12).

        Args:
            number: Month number (1-12)

        Returns:
            Month enum value

        Raises:
            ValueError: If number is not in range 1-12
        """
        if not 1 <= number <= 12:
            raise ValueError(f"Month number must be between 1 and 12, got {number}")
        return list(cls)[number - 1]

    def __str__(self) -> str:
        """Return string representation."""
        return self.value


class ExportFormat(str, Enum):
    """Supported export formats."""

    JSON = "json"
    EXCEL = "excel"
    CSV = "csv"
    MARKDOWN = "markdown"
    HTML = "html"

    @classmethod
    def from_string(cls, value: str) -> "ExportFormat":
        """
        Create ExportFormat from string value.

        Args:
            value: String representation of format

        Returns:
            ExportFormat enum value

        Raises:
            ValueError: If value doesn't match any format
        """
        value_lower = value.lower().strip()
        for fmt in cls:
            if fmt.value == value_lower or fmt.name.lower() == value_lower:
                return fmt
        valid_formats = ", ".join([f.value for f in cls])
        raise ValueError(
            f"Invalid export format: {value}. Valid formats: {valid_formats}"
        )

    def get_file_extension(self) -> str:
        """
        Get file extension for the format.

        Returns:
            File extension with dot (e.g., '.json')
        """
        extensions = {
            ExportFormat.JSON: ".json",
            ExportFormat.EXCEL: ".xlsx",
            ExportFormat.CSV: ".csv",
            ExportFormat.MARKDOWN: ".md",
            ExportFormat.HTML: ".html",
        }
        return extensions[self]

    def __str__(self) -> str:
        """Return string representation."""
        return self.value


class Environment(str, Enum):
    """Application environment types."""

    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"

    @classmethod
    def from_string(cls, value: str) -> "Environment":
        """
        Create Environment from string value.

        Args:
            value: String representation of environment

        Returns:
            Environment enum value

        Raises:
            ValueError: If value doesn't match any environment
        """
        value_lower = value.lower().strip()
        for env in cls:
            if env.value == value_lower:
                return env
        return cls.PRODUCTION  # Default to production

    def is_development(self) -> bool:
        """Check if environment is development."""
        return self == Environment.DEVELOPMENT

    def is_production(self) -> bool:
        """Check if environment is production."""
        return self == Environment.PRODUCTION

    def is_testing(self) -> bool:
        """Check if environment is testing."""
        return self == Environment.TESTING

    def __str__(self) -> str:
        """Return string representation."""
        return self.value
