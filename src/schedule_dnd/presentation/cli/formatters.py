"""
CLI output formatters using Rich.

Author: DmitrTRC
"""

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from schedule_dnd.application.dto import (
    ScheduleListItemDTO,
    ScheduleResponseDTO,
    ScheduleStatisticsDTO,
)
from schedule_dnd.domain.models import Schedule


class ScheduleFormatter:
    """Formatter for schedule display."""

    def __init__(self, console: Console) -> None:
        """
        Initialize formatter.

        Args:
            console: Rich console instance
        """
        self.console = console

    def format_schedule_table(self, schedule: Schedule) -> Table:
        """
        Format schedule as a table.

        Args:
            schedule: Schedule to format

        Returns:
            Rich Table object
        """
        table = Table(
            title=f"График дежурств - {schedule.metadata.month.display_name()} {schedule.metadata.year}",
            show_header=True,
            header_style="bold cyan",
            border_style="blue",
        )

        table.add_column("№", style="dim", width=3)
        table.add_column("Подразделение", style="cyan", min_width=30)
        table.add_column("Дата", style="green", width=12)
        table.add_column("День", style="yellow", width=12)
        table.add_column("Тип", style="magenta", width=6)
        table.add_column("Время", style="blue", width=13)

        row_num = 1
        for unit in schedule.units:
            if not unit.shifts:
                continue

            sorted_shifts = unit.get_shifts_sorted()
            for idx, shift in enumerate(sorted_shifts):
                unit_name = unit.unit_name if idx == 0 else ""

                # Color code duty type
                duty_style = self._get_duty_type_style(shift.duty_type.value)

                table.add_row(
                    str(row_num),
                    unit_name,
                    shift.date,
                    shift.get_day_of_week(),
                    Text(shift.duty_type.value, style=duty_style),
                    shift.time,
                )
                row_num += 1

        return table

    def format_schedule_list(self, schedules: list[ScheduleListItemDTO]) -> Table:
        """
        Format list of schedules.

        Args:
            schedules: List of schedule summaries

        Returns:
            Rich Table object
        """
        table = Table(
            title="Доступные графики",
            show_header=True,
            header_style="bold cyan",
            border_style="blue",
        )

        table.add_column("№", style="dim", width=3)
        table.add_column("Файл", style="cyan", min_width=25)
        table.add_column("Период", style="green", width=20)
        table.add_column("Подразд.", style="yellow", width=9)
        table.add_column("Смен", style="magenta", width=6)
        table.add_column("Создан", style="blue", width=16)

        for idx, schedule in enumerate(schedules, 1):
            period = f"{schedule.month} {schedule.year}"
            created = schedule.created_at.strftime("%d.%m.%Y %H:%M")

            table.add_row(
                str(idx),
                schedule.filename,
                period,
                str(schedule.unit_count),
                str(schedule.total_shifts),
                created,
            )

        return table

    def format_statistics(self, stats: ScheduleStatisticsDTO) -> Panel:
        """
        Format schedule statistics.

        Args:
            stats: Schedule statistics

        Returns:
            Rich Panel with statistics
        """
        content = []

        # Overall stats
        content.append(f"[bold cyan]Период:[/] {stats.month} {stats.year}")
        content.append(f"[bold cyan]Подразделений:[/] {stats.total_units}")
        content.append(f"[bold cyan]Всего смен:[/] {stats.total_shifts}")
        content.append("")

        # By duty type
        content.append("[bold yellow]По типам дежурств:[/]")
        for duty_type, count in stats.shifts_by_type.items():
            style = self._get_duty_type_style(duty_type)
            content.append(f"  [{style}]{duty_type}[/]: {count}")

        # By unit
        if stats.units:
            content.append("")
            content.append("[bold green]По подразделениям:[/]")
            for unit_stat in stats.units[:5]:  # Top 5
                content.append(
                    f"  {unit_stat.unit_name}: {unit_stat.total_shifts} смен"
                )

        return Panel(
            "\n".join(content),
            title="📊 Статистика",
            border_style="green",
            expand=False,
        )

    def format_unit_header(self, unit_idx: int, unit_name: str) -> Panel:
        """
        Format unit header.

        Args:
            unit_idx: Unit index (1-8)
            unit_name: Unit name

        Returns:
            Rich Panel
        """
        return Panel(
            f"[bold cyan]{unit_name}[/]",
            title=f"[{unit_idx}/8]",
            border_style="cyan",
            expand=False,
        )

    def format_shift_added(self, date: str, duty_type: str) -> str:
        """
        Format shift added message.

        Args:
            date: Shift date
            duty_type: Duty type

        Returns:
            Formatted message
        """
        style = self._get_duty_type_style(duty_type)
        return f"✓ Добавлено: [green]{date}[/] - [{style}]{duty_type}[/]"

    def format_error(self, message: str) -> str:
        """
        Format error message.

        Args:
            message: Error message

        Returns:
            Formatted message
        """
        return f"[bold red]✗ Ошибка:[/] {message}"

    def format_warning(self, message: str) -> str:
        """
        Format warning message.

        Args:
            message: Warning message

        Returns:
            Formatted message
        """
        return f"[bold yellow]⚠ Предупреждение:[/] {message}"

    def format_success(self, message: str) -> str:
        """
        Format success message.

        Args:
            message: Success message

        Returns:
            Formatted message
        """
        return f"[bold green]✓ {message}[/]"

    def format_info(self, message: str) -> str:
        """
        Format info message.

        Args:
            message: Info message

        Returns:
            Formatted message
        """
        return f"[bold blue]ℹ {message}[/]"

    def _get_duty_type_style(self, duty_type: str) -> str:
        """
        Get Rich style for duty type.

        Args:
            duty_type: Duty type string

        Returns:
            Rich style string
        """
        styles = {
            "ПДН": "blue",
            "ППСП": "magenta",
            "УУП": "yellow",
        }
        return styles.get(duty_type, "white")


class ExportFormatter:
    """Formatter for export results."""

    def __init__(self, console: Console) -> None:
        """
        Initialize formatter.

        Args:
            console: Rich console instance
        """
        self.console = console

    def format_export_results(self, results: list[Any]) -> Table:
        """
        Format export results.

        Args:
            results: List of ExportResultDTO

        Returns:
            Rich Table object
        """
        table = Table(
            title="Результаты экспорта",
            show_header=True,
            header_style="bold cyan",
            border_style="blue",
        )

        table.add_column("Формат", style="cyan", width=10)
        table.add_column("Статус", style="green", width=8)
        table.add_column("Файл", style="blue", min_width=30)
        table.add_column("Размер", style="yellow", width=12)

        for result in results:
            status = "✓ OK" if result.success else "✗ Fail"
            status_style = "green" if result.success else "red"

            size = (
                self._format_file_size(result.file_size) if result.file_size else "N/A"
            )

            table.add_row(
                result.format.upper(),
                Text(status, style=status_style),
                result.output_path if result.success else result.error or "N/A",
                size,
            )

        return table

    def _format_file_size(self, size_bytes: int) -> str:
        """
        Format file size.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted size string
        """
        for unit in ["B", "KB", "MB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} GB"
