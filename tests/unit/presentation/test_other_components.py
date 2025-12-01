"""
Unit tests for other CLI components.

This module tests formatters and other presentation utilities.
Author: DmitrTRC
"""

from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

import pytest

from schedule_dnd.domain.enums import DutyType, ExportFormat, Month
from schedule_dnd.domain.models import Schedule, ScheduleMetadata, Shift, Unit

# ========== Test ScheduleFormatter ==========


class TestScheduleFormatter:
    """Tests for ScheduleFormatter."""

    @pytest.fixture
    def formatter(self):
        """Create ScheduleFormatter instance."""
        from schedule_dnd.presentation.cli.formatters import ScheduleFormatter

        console = Mock()
        return ScheduleFormatter(console)

    @pytest.fixture
    def sample_schedule(self):
        """Create sample schedule for testing."""
        metadata = ScheduleMetadata(
            document_type="График дежурств",
            month=Month.OCTOBER,
            year=2025,
            created_at=datetime(2025, 10, 1, 10, 0, 0),
            created_by="Test User",
        )

        unit = Unit(
            id=1,
            unit_name="ДНД «Всеволожский дозор»",
            shifts=[
                Shift(
                    date="01.10.2025",
                    duty_type=DutyType.PDN,
                    time="09:00-18:00",
                    notes="Test note",
                )
            ],
        )

        return Schedule(metadata=metadata, units=[unit])

    def test_format_unit_header(self, formatter):
        """Test formatting unit header."""
        from rich.panel import Panel

        result = formatter.format_unit_header(1, "ДНД «Всеволожский дозор»")

        assert isinstance(result, Panel)

    def test_format_shift_added(self, formatter):
        """Test formatting shift added message."""
        result = formatter.format_shift_added("01.10.2025", "ПДН")

        assert isinstance(result, str)
        assert "01.10.2025" in result

    def test_format_schedule_table(self, formatter, sample_schedule):
        """Test formatting schedule as table."""
        from rich.table import Table

        result = formatter.format_schedule_table(sample_schedule)

        assert isinstance(result, Table)


# ========== Test ExportFormatter ==========


class TestExportFormatter:
    """Tests for ExportFormatter."""

    @pytest.fixture
    def formatter(self):
        """Create ExportFormatter instance."""
        from schedule_dnd.presentation.cli.formatters import ExportFormatter

        console = Mock()
        return ExportFormatter(console)

    def test_format_export_results_success(self, formatter):
        """Test formatting successful export results."""
        from rich.table import Table

        from schedule_dnd.application.dto import ExportResultDTO

        results = [
            ExportResultDTO(
                success=True,
                format=ExportFormat.JSON.value,
                output_path="/tmp/schedule.json",
                file_size=1024,
            )
        ]

        output = formatter.format_export_results(results)

        assert isinstance(output, Table)

    def test_format_export_results_failure(self, formatter):
        """Test formatting failed export results."""
        from rich.table import Table

        from schedule_dnd.application.dto import ExportResultDTO

        results = [
            ExportResultDTO(
                success=False,
                format=ExportFormat.JSON.value,
                output_path="N/A",
                error="Test error",
            )
        ]

        output = formatter.format_export_results(results)

        assert isinstance(output, Table)

    def test_format_export_results_multiple(self, formatter):
        """Test formatting multiple export results."""
        from rich.table import Table

        from schedule_dnd.application.dto import ExportResultDTO

        results = [
            ExportResultDTO(
                success=True,
                format=ExportFormat.JSON.value,
                output_path="/tmp/schedule.json",
                file_size=1024,
            ),
            ExportResultDTO(
                success=True,
                format=ExportFormat.EXCEL.value,
                output_path="/tmp/schedule.xlsx",
                file_size=2048,
            ),
        ]

        output = formatter.format_export_results(results)

        assert isinstance(output, Table)


# ========== Test BaseCommand ==========


class TestBaseCommand:
    """Tests for BaseCommand."""

    @pytest.fixture
    def concrete_command(self):
        """Create a concrete implementation of BaseCommand for testing."""
        from unittest.mock import patch

        from schedule_dnd.presentation.cli.commands.base import BaseCommand

        class ConcreteCommand(BaseCommand):
            """Concrete implementation for testing."""

            def execute(self, *args, **kwargs) -> int:
                """Execute command."""
                return 0

        with patch("schedule_dnd.presentation.cli.commands.base.get_settings"):
            return ConcreteCommand()

    def test_base_command_init(self, concrete_command):
        """Test BaseCommand initialization."""
        assert concrete_command.console is not None
        assert concrete_command.settings is not None

    def test_base_command_success(self, concrete_command):
        """Test BaseCommand success method."""
        concrete_command.console.print = Mock()

        concrete_command.success("Test message")

        concrete_command.console.print.assert_called_once()

    def test_base_command_error(self, concrete_command):
        """Test BaseCommand error method."""
        concrete_command.console.print = Mock()

        concrete_command.error("Test error")

        concrete_command.console.print.assert_called_once()

    def test_base_command_warning(self, concrete_command):
        """Test BaseCommand warning method."""
        concrete_command.console.print = Mock()

        concrete_command.warning("Test warning")

        concrete_command.console.print.assert_called_once()


# ========== Test Logging ==========


class TestLogging:
    """Tests for logging module."""

    def test_setup_logging_basic(self):
        """Test setup_logging function."""
        from pathlib import Path
        from tempfile import mkdtemp

        from schedule_dnd.infrastructure.logging import get_logger, setup_logging

        # setup_logging returns None, but configures logging
        temp_dir = Path(mkdtemp())
        log_file = temp_dir / "test.log"

        result = setup_logging(log_file=log_file)

        # Verify that setup_logging returns None
        assert result is None

        # Verify that we can get a logger after setup
        logger = get_logger("test_logger")
        assert logger is not None

    def test_get_logger(self):
        """Test get_logger function."""
        from schedule_dnd.infrastructure.logging import get_logger

        logger = get_logger(__name__)

        assert logger is not None
