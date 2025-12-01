"""
Unit tests for CLIApp.

This module tests the main CLI application.
Author: DmitrTRC
"""

from unittest.mock import Mock, patch

import pytest

from schedule_dnd.presentation.cli.app import CLIApp, create_app, fix_terminal_encoding

# ========== Test fix_terminal_encoding() ==========


class TestFixTerminalEncoding:
    """Tests for fix_terminal_encoding function."""

    @patch("locale.setlocale")
    @patch("sys.stdin")
    @patch("sys.stdout")
    @patch("sys.stderr")
    def test_fix_terminal_encoding_success(
        self, mock_stderr, mock_stdout, mock_stdin, mock_setlocale
    ):
        """Test fix_terminal_encoding with successful locale setting."""
        mock_stdin.encoding = "cp1252"
        mock_stdout.encoding = "cp1252"
        mock_stderr.encoding = "cp1252"

        mock_stdin.reconfigure = Mock()
        mock_stdout.reconfigure = Mock()
        mock_stderr.reconfigure = Mock()

        fix_terminal_encoding()

        mock_stdin.reconfigure.assert_called_once_with(encoding="utf-8")
        mock_stdout.reconfigure.assert_called_once_with(encoding="utf-8")
        mock_stderr.reconfigure.assert_called_once_with(encoding="utf-8")


# ========== Test create_app() ==========


class TestCreateApp:
    """Tests for create_app factory function."""

    @patch("schedule_dnd.presentation.cli.app.fix_terminal_encoding")
    @patch("schedule_dnd.presentation.cli.app.get_settings")
    def test_create_app(self, mock_get_settings, mock_fix_encoding):
        """Test create_app creates CLIApp instance."""
        app = create_app()

        assert isinstance(app, CLIApp)
        mock_fix_encoding.assert_called_once()


# ========== Test CLIApp ==========


@pytest.fixture
def mock_settings():
    """Create mock settings."""
    settings = Mock()
    settings.debug = False
    return settings


@pytest.fixture
def cli_app(mock_settings):
    """Create CLIApp instance with mocked dependencies."""
    with patch("schedule_dnd.presentation.cli.app.fix_terminal_encoding"):
        with patch(
            "schedule_dnd.presentation.cli.app.get_settings", return_value=mock_settings
        ):
            app = CLIApp()
            app.console.print = Mock()
            return app


class TestCLIAppInit:
    """Tests for CLIApp initialization."""

    @patch("schedule_dnd.presentation.cli.app.fix_terminal_encoding")
    @patch("schedule_dnd.presentation.cli.app.get_settings")
    def test_init(self, mock_get_settings, mock_fix_encoding):
        """Test CLIApp initialization."""
        app = CLIApp()

        assert app.running is True
        assert app.console is not None
        assert app.settings is not None
        mock_fix_encoding.assert_called_once()


class TestCLIAppRun:
    """Tests for CLIApp.run()"""

    @patch("builtins.input")
    def test_run_exit_immediately(self, mock_input, cli_app):
        """Test run with immediate exit."""
        mock_input.return_value = "0"

        result = cli_app.run()

        assert result == 0
        assert cli_app.running is False

    @patch("builtins.input")
    def test_run_keyboard_interrupt(self, mock_input, cli_app):
        """Test run with keyboard interrupt."""
        mock_input.side_effect = KeyboardInterrupt()

        result = cli_app.run()

        assert result == 130

    @patch("builtins.input")
    def test_run_exception_production_mode(self, mock_input, cli_app):
        """Test run with exception in production mode."""
        cli_app.settings.debug = False
        mock_input.side_effect = Exception("Test error")

        result = cli_app.run()

        assert result == 1

    @patch("builtins.input")
    def test_run_invalid_choice(self, mock_input, cli_app):
        """Test run with invalid menu choice."""
        mock_input.side_effect = ["99", "0"]

        result = cli_app.run()

        assert result == 0


class TestCLIAppPrivateMethods:
    """Tests for CLIApp private methods."""

    def test_show_welcome(self, cli_app):
        """Test _show_welcome displays welcome message."""
        cli_app._show_welcome()

        assert cli_app.console.print.called
        assert cli_app.console.print.call_count >= 2

    def test_show_goodbye(self, cli_app):
        """Test _show_goodbye displays goodbye message."""
        cli_app._show_goodbye()

        assert cli_app.console.print.called

    def test_show_menu(self, cli_app):
        """Test _show_menu displays menu."""
        cli_app._show_menu()

        assert cli_app.console.print.called

    @patch("builtins.input")
    def test_get_menu_choice(self, mock_input, cli_app):
        """Test _get_menu_choice gets user input."""
        mock_input.return_value = "1"

        choice = cli_app._get_menu_choice()

        assert choice == "1"
        mock_input.assert_called_once()
