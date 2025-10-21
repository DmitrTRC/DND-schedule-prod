"""
Unit tests for domain enums.

Author: DmitrTRC
"""

import pytest

from schedule_dnd.domain.enums import DutyType, Environment, ExportFormat, Month


class TestDutyType:
    """Test cases for DutyType enum."""

    def test_all_duty_types_exist(self) -> None:
        """Test that all duty types are defined."""
        assert DutyType.PDN.value == "ПДН"
        assert DutyType.PPSP.value == "ППСП"
        assert DutyType.UUP.value == "УУП"

    def test_from_string_valid(self) -> None:
        """Test converting valid strings to DutyType."""
        assert DutyType.from_string("ПДН") == DutyType.PDN
        assert DutyType.from_string("пдн") == DutyType.PDN
        assert DutyType.from_string("  ппсп  ") == DutyType.PPSP

    def test_from_string_by_name(self) -> None:
        """Test converting by enum name."""
        assert DutyType.from_string("PDN") == DutyType.PDN
        assert DutyType.from_string("pdn") == DutyType.PDN

    def test_from_string_invalid(self) -> None:
        """Test that invalid string raises error."""
        with pytest.raises(ValueError, match="Invalid duty type"):
            DutyType.from_string("INVALID")

    def test_str_representation(self) -> None:
        """Test string representation."""
        assert str(DutyType.PDN) == "ПДН"
        assert str(DutyType.PPSP) == "ППСП"
        assert str(DutyType.UUP) == "УУП"


class TestMonth:
    """Test cases for Month enum."""

    def test_all_months_exist(self) -> None:
        """Test that all 12 months are defined."""
        assert len(list(Month)) == 12
        assert Month.JANUARY.value == "январь"
        assert Month.DECEMBER.value == "декабрь"

    def test_from_string_valid(self) -> None:
        """Test converting valid month names."""
        assert Month.from_string("октябрь") == Month.OCTOBER
        assert Month.from_string("ОКТЯБРЬ") == Month.OCTOBER
        assert Month.from_string("  январь  ") == Month.JANUARY

    def test_from_string_invalid(self) -> None:
        """Test that invalid month raises error."""
        with pytest.raises(ValueError, match="Invalid month"):
            Month.from_string("invalid")

    def test_to_number(self) -> None:
        """Test converting month to number."""
        assert Month.JANUARY.to_number() == 1
        assert Month.OCTOBER.to_number() == 10
        assert Month.DECEMBER.to_number() == 12

    def test_from_number_valid(self) -> None:
        """Test creating month from number."""
        assert Month.from_number(1) == Month.JANUARY
        assert Month.from_number(10) == Month.OCTOBER
        assert Month.from_number(12) == Month.DECEMBER

    def test_from_number_invalid(self) -> None:
        """Test that invalid number raises error."""
        with pytest.raises(ValueError, match="must be between 1 and 12"):
            Month.from_number(0)

        with pytest.raises(ValueError, match="must be between 1 and 12"):
            Month.from_number(13)

    def test_str_representation(self) -> None:
        """Test string representation."""
        assert str(Month.OCTOBER) == "октябрь"


class TestExportFormat:
    """Test cases for ExportFormat enum."""

    def test_all_formats_exist(self) -> None:
        """Test that all export formats are defined."""
        assert ExportFormat.JSON.value == "json"
        assert ExportFormat.EXCEL.value == "excel"
        assert ExportFormat.CSV.value == "csv"
        assert ExportFormat.MARKDOWN.value == "markdown"
        assert ExportFormat.HTML.value == "html"

    def test_from_string_valid(self) -> None:
        """Test converting valid strings to ExportFormat."""
        assert ExportFormat.from_string("json") == ExportFormat.JSON
        assert ExportFormat.from_string("JSON") == ExportFormat.JSON
        assert ExportFormat.from_string("Excel") == ExportFormat.EXCEL

    def test_from_string_invalid(self) -> None:
        """Test that invalid format raises error."""
        with pytest.raises(ValueError, match="Invalid export format"):
            ExportFormat.from_string("pdf")

    def test_get_file_extension(self) -> None:
        """Test getting file extension for each format."""
        assert ExportFormat.JSON.get_file_extension() == ".json"
        assert ExportFormat.EXCEL.get_file_extension() == ".xlsx"
        assert ExportFormat.CSV.get_file_extension() == ".csv"
        assert ExportFormat.MARKDOWN.get_file_extension() == ".md"
        assert ExportFormat.HTML.get_file_extension() == ".html"

    def test_str_representation(self) -> None:
        """Test string representation."""
        assert str(ExportFormat.JSON) == "json"


class TestEnvironment:
    """Test cases for Environment enum."""

    def test_all_environments_exist(self) -> None:
        """Test that all environments are defined."""
        assert Environment.DEVELOPMENT.value == "development"
        assert Environment.PRODUCTION.value == "production"
        assert Environment.TESTING.value == "testing"

    def test_from_string_valid(self) -> None:
        """Test converting valid strings to Environment."""
        assert Environment.from_string("development") == Environment.DEVELOPMENT
        assert Environment.from_string("PRODUCTION") == Environment.PRODUCTION

    def test_from_string_invalid_defaults_production(self) -> None:
        """Test that invalid environment defaults to production."""
        assert Environment.from_string("invalid") == Environment.PRODUCTION

    def test_is_development(self) -> None:
        """Test checking if environment is development."""
        assert Environment.DEVELOPMENT.is_development() is True
        assert Environment.PRODUCTION.is_development() is False

    def test_is_production(self) -> None:
        """Test checking if environment is production."""
        assert Environment.PRODUCTION.is_production() is True
        assert Environment.DEVELOPMENT.is_production() is False

    def test_is_testing(self) -> None:
        """Test checking if environment is testing."""
        assert Environment.TESTING.is_testing() is True
        assert Environment.PRODUCTION.is_testing() is False

    def test_str_representation(self) -> None:
        """Test string representation."""
        assert str(Environment.DEVELOPMENT) == "development"
