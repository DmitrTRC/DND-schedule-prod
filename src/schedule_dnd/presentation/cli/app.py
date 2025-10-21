"""
Main CLI application.

Author: DmitrTRC
"""

import sys
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from schedule_dnd.domain.constants import APP_NAME, APP_VERSION
from schedule_dnd.infrastructure.config.settings import get_settings


class CLIApp:
    """Main CLI application."""

    def __init__(self) -> None:
        """Initialize CLI application."""
        self.console = Console()
        self.settings = get_settings()
        self.running = True

    def run(self) -> int:
        """
        Run the CLI application.

        Returns:
            Exit code
        """
        try:
            self._show_welcome()

            while self.running:
                self._show_menu()
                choice = self._get_menu_choice()

                if choice == "0":
                    self.running = False
                    self._show_goodbye()
                elif choice == "1":
                    self._handle_create_schedule()
                elif choice == "2":
                    self._handle_load_schedule()
                elif choice == "3":
                    self._handle_list_schedules()
                elif choice == "4":
                    self._handle_export_schedule()
                else:
                    self.console.print(
                        "❌ Неверный выбор. Попробуйте снова.", style="bold red"
                    )

            return 0

        except KeyboardInterrupt:
            self.console.print("\n\n👋 Работа прервана пользователем.")
            return 130
        except Exception as e:
            self.console.print(f"\n❌ Ошибка: {e}", style="bold red")
            if self.settings.debug:
                import traceback

                traceback.print_exc()
            return 1

    def _show_welcome(self) -> None:
        """Show welcome message."""
        welcome = Panel(
            f"[bold cyan]{APP_NAME}[/bold cyan]\n"
            f"[dim]Версия {APP_VERSION}[/dim]\n\n"
            f"[yellow]Система управления графиками дежурств ДНД[/yellow]",
            border_style="cyan",
            expand=False,
        )
        self.console.print()
        self.console.print(welcome)
        self.console.print()

    def _show_goodbye(self) -> None:
        """Show goodbye message."""
        self.console.print()
        self.console.print(
            Panel(
                "[bold green]Спасибо за использование Schedule DND![/bold green]\n"
                "[dim]До встречи![/dim]",
                border_style="green",
                expand=False,
            )
        )

    def _show_menu(self) -> None:
        """Show main menu."""
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column(style="cyan bold", width=3)
        table.add_column(style="white")

        table.add_row("1", "📝 Создать новый график")
        table.add_row("2", "📂 Загрузить существующий график")
        table.add_row("3", "📋 Список всех графиков")
        table.add_row("4", "💾 Экспорт графика")
        table.add_row("0", "🚪 Выход")

        self.console.print()
        self.console.print(
            Panel(
                table,
                title="[bold]Главное меню[/bold]",
                border_style="blue",
            )
        )

    def _get_menu_choice(self) -> str:
        """Get user's menu choice."""
        return input("\n👉 Ваш выбор: ").strip()

    def _handle_create_schedule(self) -> None:
        """Handle create schedule command."""
        from schedule_dnd.presentation.cli.commands.create import CreateCommand

        command = CreateCommand()
        command.execute()

    def _handle_load_schedule(self) -> None:
        """Handle load schedule command."""
        from schedule_dnd.presentation.cli.commands.load import LoadCommand

        command = LoadCommand()
        command.execute()

    def _handle_list_schedules(self) -> None:
        """Handle list schedules command."""
        self.console.print("\n📋 [bold]Доступные графики:[/bold]\n")

        from schedule_dnd.infrastructure.repositories.json_repository import (
            JSONRepository,
        )

        repo = JSONRepository()
        schedules = repo.list_schedules()

        if not schedules:
            self.console.print("[yellow]Графики не найдены.[/yellow]")
            return

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim", width=4)
        table.add_column("Файл", style="cyan")
        table.add_column("Дата изменения", style="green")

        for idx, filepath in enumerate(schedules, 1):
            from datetime import datetime

            mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
            table.add_row(str(idx), filepath.name, mtime.strftime("%d.%m.%Y %H:%M"))

        self.console.print(table)

    def _handle_export_schedule(self) -> None:
        """Handle export schedule command."""
        from schedule_dnd.presentation.cli.commands.export import ExportCommand

        command = ExportCommand()
        command.execute()


def create_app() -> CLIApp:
    """
    Create CLI application instance.

    Returns:
        CLI application
    """
    return CLIApp()
