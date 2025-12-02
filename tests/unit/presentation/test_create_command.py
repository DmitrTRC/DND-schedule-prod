"""
Unit tests for CreateCommand.

This module tests the create command for interactive schedule creation.
Author: DmitrTRC
"""

from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from schedule_dnd.domain.enums import DutyType, ExportFormat, Month

# ========== Test CreateCommand ==========


class TestCreateCommand:
    """Tests for CreateCommand."""

    @patch("builtins.input")
    @patch("schedule_dnd.presentation.cli.commands.create.IntPrompt.ask")
    @patch("schedule_dnd.presentation.cli.commands.create.Confirm.ask")
    @patch("schedule_dnd.presentation.cli.commands.create.BaseCommand.__init__")
    def test_execute_success_minimal(
        self, mock_base_init, mock_confirm, mock_int_prompt, mock_input
    ):
        """Test successful execution with minimal input (no shifts)."""
        from schedule_dnd.presentation.cli.commands.create import CreateCommand

        # Setup
        mock_base_init.return_value = None
        cmd = CreateCommand()
        cmd.console = Mock()
        cmd.settings = Mock()
        cmd.schedule_service = Mock()
        cmd.export_service = Mock()
        cmd.repository = Mock()

        mock_int_prompt.side_effect = [10, 2025]  # месяц (октябрь=10), год
        mock_input.return_value = ""  # Empty input - no shifts for all units
        mock_confirm.return_value = True  # Continue through all units

        result = cmd.execute()

        # Should fail because no shifts added across all units
        assert result == 1

    @patch("schedule_dnd.presentation.cli.commands.create.IntPrompt.ask")
    @patch("schedule_dnd.presentation.cli.commands.create.Confirm.ask")
    @patch("builtins.input")
    @patch("schedule_dnd.presentation.cli.commands.create.BaseCommand.__init__")
    def test_execute_success_with_shifts(
        self, mock_base_init, mock_input, mock_confirm, mock_int_prompt
    ):
        """Test successful execution with shifts."""
        from schedule_dnd.application.dto import ValidationResultDTO
        from schedule_dnd.presentation.cli.commands.create import CreateCommand

        # Setup
        mock_base_init.return_value = None
        cmd = CreateCommand()
        cmd.console = Mock()
        cmd.settings = Mock(debug=False, data_dir=Path("/tmp"))
        cmd.schedule_service = Mock()
        cmd.export_service = Mock()
        cmd.repository = Mock()

        # Setup validation
        validation_result = ValidationResultDTO(is_valid=True, errors=[], warnings=[])
        cmd.schedule_service.validate_schedule.return_value = validation_result

        # Setup response
        response = Mock()
        response.metadata.month = "октябрь"
        response.metadata.year = 2025
        cmd.schedule_service.create_schedule.return_value = response

        mock_int_prompt.side_effect = [10, 2025]  # месяц (октябрь=10), год
        mock_input.side_effect = [
            "15",
            "1",
            "",  # Unit 1: день 15, тип 1 (ПДН), завершить
            "",
            "",
            "",
            "",
            "",
            "",
            "",  # Units 2-8: пусто (нет смен)
        ]
        # 7 раз "Продолжить?" после юнитов 1-7, затем "Экспортировать?" - False
        mock_confirm.side_effect = [True] * 7 + [False]

        result = cmd.execute()

        assert result == 0

    @patch("schedule_dnd.presentation.cli.commands.create.IntPrompt.ask")
    @patch("schedule_dnd.presentation.cli.commands.create.BaseCommand.__init__")
    def test_execute_keyboard_interrupt(self, mock_base_init, mock_int_prompt):
        """Test execution with KeyboardInterrupt."""
        from schedule_dnd.presentation.cli.commands.create import CreateCommand

        mock_base_init.return_value = None
        cmd = CreateCommand()
        cmd.console = Mock()

        mock_int_prompt.side_effect = KeyboardInterrupt()

        result = cmd.execute()

        assert result == 130


# ========== Test _input_period() ==========


class TestInputPeriod:
    """Tests for CreateCommand._input_period()"""

    @patch("schedule_dnd.presentation.cli.commands.create.IntPrompt.ask")
    @patch("schedule_dnd.presentation.cli.commands.create.BaseCommand.__init__")
    def test_input_period_success(self, mock_base_init, mock_int_prompt):
        """Test successful period input."""
        from schedule_dnd.presentation.cli.commands.create import CreateCommand

        mock_base_init.return_value = None
        cmd = CreateCommand()
        cmd.console = Mock()

        mock_int_prompt.side_effect = [10, 2025]  # месяц (октябрь=10), год

        month, year = cmd._input_period()

        assert month == Month.OCTOBER
        assert year == 2025


# ========== Test _input_shifts_for_unit() ==========


class TestInputShiftsForUnit:
    """Tests for CreateCommand._input_shifts_for_unit()"""

    @patch("builtins.input")
    @patch("schedule_dnd.presentation.cli.commands.create.BaseCommand.__init__")
    def test_input_shifts_empty(self, mock_base_init, mock_input):
        """Test input shifts with immediate 'готово'."""
        from schedule_dnd.presentation.cli.commands.create import CreateCommand

        mock_base_init.return_value = None
        cmd = CreateCommand()
        cmd.console = Mock()

        mock_input.return_value = ""  # Empty input to finish

        shifts = cmd._input_shifts_for_unit(
            "ДНД «Всеволожский дозор»", Month.OCTOBER, 2025
        )

        assert len(shifts) == 0

    @patch("builtins.input")
    @patch("schedule_dnd.presentation.cli.commands.create.BaseCommand.__init__")
    def test_input_shifts_single_shift(self, mock_base_init, mock_input):
        """Test input single shift."""
        from schedule_dnd.presentation.cli.commands.create import CreateCommand

        mock_base_init.return_value = None
        cmd = CreateCommand()
        cmd.console = Mock()

        # First call: day "15", second call: duty type "1", third call: empty to finish
        mock_input.side_effect = ["15", "1", ""]

        shifts = cmd._input_shifts_for_unit(
            "ДНД «Всеволожский дозор»", Month.OCTOBER, 2025
        )

        assert len(shifts) == 1
        assert shifts[0].date == "15.10.2025"
        assert shifts[0].duty_type == DutyType.PDN


# ========== Test _export_schedule() ==========


class TestExportSchedule:
    """Tests for CreateCommand._export_schedule()"""

    @patch("builtins.input")
    @patch("schedule_dnd.presentation.cli.commands.create.BaseCommand.__init__")
    def test_export_schedule_json(self, mock_base_init, mock_input):
        """Test export to JSON format."""
        from schedule_dnd.presentation.cli.commands.create import CreateCommand

        mock_base_init.return_value = None
        cmd = CreateCommand()
        cmd.console = Mock()
        cmd.settings = Mock(data_dir=Path("/tmp"))
        cmd.export_service = Mock()
        cmd.repository = Mock()

        # Setup repository
        schedule = Mock()
        cmd.repository.load.return_value = schedule

        # Setup export result - all fields must be concrete values for Rich rendering
        result = Mock()
        result.success = True
        result.format = "json"  # Must be string, not Mock
        result.output_path = "/tmp/schedule.json"  # Must be string
        result.error = None
        result.file_size = 1024  # Must be int
        cmd.export_service.export_schedule.return_value = result

        mock_input.return_value = "1"

        response = Mock()
        response.metadata.year = 2025
        response.metadata.month.to_number.return_value = 10

        cmd._export_schedule(response)

        cmd.export_service.export_schedule.assert_called_once()

    @patch("builtins.input")
    @patch("schedule_dnd.presentation.cli.commands.create.BaseCommand.__init__")
    def test_export_schedule_all_formats(self, mock_base_init, mock_input):
        """Test export to all formats."""
        from schedule_dnd.presentation.cli.commands.create import CreateCommand

        mock_base_init.return_value = None
        cmd = CreateCommand()
        cmd.console = Mock()
        cmd.settings = Mock(data_dir=Path("/tmp"))
        cmd.export_service = Mock()
        cmd.repository = Mock()

        schedule = Mock()
        cmd.repository.load.return_value = schedule

        # Setup export result - all fields must be concrete values for Rich rendering
        result = Mock()
        result.success = True
        result.format = "json"  # Must be string, not Mock
        result.output_path = "/tmp/schedule.json"  # Must be string
        result.error = None
        result.file_size = 2048  # Must be int
        cmd.export_service.export_to_all_formats.return_value = [result]

        mock_input.return_value = "6"

        response = Mock()
        response.metadata.year = 2025
        response.metadata.month.to_number.return_value = 10

        cmd._export_schedule(response)

        cmd.export_service.export_to_all_formats.assert_called_once()
