#!/usr/bin/env python3
"""
Quick test script for CLI commands.

Tests all commands without interactive input.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rich.console import Console

console = Console()


def test_imports():
    """Test that all modules can be imported."""
    console.print("\n[bold cyan]Testing imports...[/bold cyan]")

    try:
        # Domain
        from schedule_dnd.domain.enums import DutyType, ExportFormat, Month
        from schedule_dnd.domain.models import Schedule, ScheduleMetadata, Shift, Unit

        console.print("✓ Domain imports OK")

        # Application
        from schedule_dnd.application.dto import ScheduleCreateDTO
        from schedule_dnd.application.services.export_service import ExportService
        from schedule_dnd.application.services.schedule_service import ScheduleService

        console.print("✓ Application imports OK")

        # Infrastructure
        from schedule_dnd.infrastructure.config.settings import get_settings
        from schedule_dnd.infrastructure.exporters.factory import ExporterFactory
        from schedule_dnd.infrastructure.repositories.json_repository import (
            JSONRepository,
        )

        console.print("✓ Infrastructure imports OK")

        # Presentation
        from schedule_dnd.presentation.cli.app import CLIApp
        from schedule_dnd.presentation.cli.commands.create import CreateCommand
        from schedule_dnd.presentation.cli.commands.export import ExportCommand
        from schedule_dnd.presentation.cli.commands.load import LoadCommand
        from schedule_dnd.presentation.cli.formatters import (
            ExportFormatter,
            ScheduleFormatter,
        )

        console.print("✓ Presentation imports OK")

        console.print("\n[bold green]✓ All imports successful![/bold green]")
        return True

    except Exception as e:
        console.print(f"\n[bold red]✗ Import error: {e}[/bold red]")
        import traceback

        traceback.print_exc()
        return False


def test_command_creation():
    """Test that commands can be instantiated."""
    console.print("\n[bold cyan]Testing command creation...[/bold cyan]")

    try:
        from rich.console import Console

        from schedule_dnd.application.services.export_service import ExportService
        from schedule_dnd.application.services.schedule_service import ScheduleService
        from schedule_dnd.infrastructure.config.settings import get_settings
        from schedule_dnd.infrastructure.repositories.json_repository import (
            JSONRepository,
        )
        from schedule_dnd.presentation.cli.commands.create import CreateCommand
        from schedule_dnd.presentation.cli.commands.export import ExportCommand
        from schedule_dnd.presentation.cli.commands.load import LoadCommand

        settings = get_settings()
        repo = JSONRepository()
        schedule_service = ScheduleService(repo)
        export_service = ExportService(repo)
        test_console = Console()

        # Create commands
        create_cmd = CreateCommand(
            test_console, settings, schedule_service, export_service, repo
        )
        load_cmd = LoadCommand(
            test_console, settings, schedule_service, export_service, repo
        )
        export_cmd = ExportCommand(
            test_console, settings, schedule_service, export_service, repo
        )

        console.print("✓ CreateCommand instantiated")
        console.print("✓ LoadCommand instantiated")
        console.print("✓ ExportCommand instantiated")

        console.print("\n[bold green]✓ All commands created successfully![/bold green]")
        return True

    except Exception as e:
        console.print(f"\n[bold red]✗ Command creation error: {e}[/bold red]")
        import traceback

        traceback.print_exc()
        return False


def test_formatters():
    """Test formatters."""
    console.print("\n[bold cyan]Testing formatters...[/bold cyan]")

    try:
        from datetime import datetime

        from schedule_dnd.application.dto import ScheduleListItemDTO
        from schedule_dnd.presentation.cli.formatters import (
            ExportFormatter,
            ScheduleFormatter,
        )

        test_console = Console()
        schedule_formatter = ScheduleFormatter(test_console)
        export_formatter = ExportFormatter(test_console)

        # Test basic formatting
        msg = schedule_formatter.format_success("Test message")
        console.print("✓ ScheduleFormatter.format_success()")

        msg = schedule_formatter.format_error("Error message")
        console.print("✓ ScheduleFormatter.format_error()")

        msg = schedule_formatter.format_warning("Warning message")
        console.print("✓ ScheduleFormatter.format_warning()")

        # Test list formatting
        test_items = [
            ScheduleListItemDTO(
                filename="test.json",
                month="октябрь",
                year=2025,
                unit_count=8,
                total_shifts=45,
                created_at=datetime.now(),
            )
        ]
        table = schedule_formatter.format_schedule_list(test_items)
        console.print("✓ ScheduleFormatter.format_schedule_list()")

        console.print("\n[bold green]✓ All formatters working![/bold green]")
        return True

    except Exception as e:
        console.print(f"\n[bold red]✗ Formatter error: {e}[/bold red]")
        import traceback

        traceback.print_exc()
        return False


def test_app_creation():
    """Test that app can be created."""
    console.print("\n[bold cyan]Testing app creation...[/bold cyan]")

    try:
        from schedule_dnd.presentation.cli.app import create_app

        app = create_app()
        console.print("✓ App created successfully")

        # Check app has methods
        assert hasattr(app, "run"), "App missing run() method"
        assert hasattr(app, "show_menu"), "App missing show_menu() method"
        console.print("✓ App has required methods")

        console.print("\n[bold green]✓ App creation successful![/bold green]")
        return True

    except Exception as e:
        console.print(f"\n[bold red]✗ App creation error: {e}[/bold red]")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    console.print(
        "\n[bold magenta]═══════════════════════════════════════[/bold magenta]"
    )
    console.print("[bold magenta]   Phase 3 CLI Testing Suite[/bold magenta]")
    console.print(
        "[bold magenta]═══════════════════════════════════════[/bold magenta]\n"
    )

    results = []

    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Command Creation", test_command_creation()))
    results.append(("Formatters", test_formatters()))
    results.append(("App Creation", test_app_creation()))

    # Summary
    console.print(
        "\n[bold magenta]═══════════════════════════════════════[/bold magenta]"
    )
    console.print("[bold cyan]Test Results Summary:[/bold cyan]\n")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[green]✓ PASS[/green]" if result else "[red]✗ FAIL[/red]"
        console.print(f"  {status} - {name}")

    console.print(f"\n[bold]Total: {passed}/{total} tests passed[/bold]")

    if passed == total:
        console.print(
            "\n[bold green]🎉 All tests passed! CLI is ready to use![/bold green]"
        )
        console.print("\n[dim]Run the application with:[/dim]")
        console.print("[cyan]  python -m schedule_dnd[/cyan]")
        return 0
    else:
        console.print(
            "\n[bold red]Some tests failed. Please review errors above.[/bold red]"
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
