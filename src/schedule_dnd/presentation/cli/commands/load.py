"""
Load command - load and display existing schedules.

Author: DmitrTRC
"""

from rich.prompt import Confirm, IntPrompt

from schedule_dnd.presentation.cli.commands.base import BaseCommand
from schedule_dnd.presentation.cli.formatters import ScheduleFormatter


class LoadCommand(BaseCommand):
    """Command for loading existing schedules."""

    def execute(self) -> int:
        """
        Execute load command.

        Returns:
            Exit code
        """
        self.console.print("\n[bold cyan]Загрузка графика[/bold cyan]\n")

        try:
            # Step 1: List available schedules
            schedules = self.schedule_service.list_schedules()

            if not schedules:
                self.warning("Графики не найдены")
                self.info(
                    f"Создайте новый график или поместите файлы в {self.settings.data_dir}"
                )
                return 0

            # Step 2: Show list
            formatter = ScheduleFormatter(self.console)
            self.console.print(formatter.format_schedule_list(schedules))

            # Step 3: Select schedule
            choice = IntPrompt.ask(
                "\nВыберите график (номер)",
                default=1,
            )

            if not 1 <= choice <= len(schedules):
                self.error(f"Неверный номер: {choice}")
                return 1

            selected = schedules[choice - 1]

            # Step 4: Load schedule
            self.console.print(f"\n[dim]Загрузка {selected.filename}...[/dim]")

            schedule_response = self.schedule_service.get_schedule(selected.filename)

            # Step 5: Display schedule
            self.console.print()

            # Convert response to domain model for display
            from datetime import datetime

            from schedule_dnd.domain.enums import DutyType, Month
            from schedule_dnd.domain.models import (
                Schedule,
                ScheduleMetadata,
                Shift,
                Unit,
            )

            metadata = ScheduleMetadata(
                month=Month.from_string(schedule_response.metadata.month),
                year=schedule_response.metadata.year,
                created_at=schedule_response.metadata.created_at,
                created_by=schedule_response.metadata.created_by,
                source=schedule_response.metadata.source,
                signatory=schedule_response.metadata.signatory,
                note=schedule_response.metadata.note,
            )

            units = []
            for unit_dto in schedule_response.schedule:
                shifts = [
                    Shift(
                        date=shift.date,
                        duty_type=DutyType(shift.duty_type),
                        time=shift.time,
                        notes=shift.notes,
                    )
                    for shift in unit_dto.shifts
                ]
                unit = Unit(id=unit_dto.id, unit_name=unit_dto.unit_name, shifts=shifts)
                units.append(unit)

            schedule = Schedule(metadata=metadata, units=units)

            # Show table
            table = formatter.format_schedule_table(schedule)
            self.console.print(table)

            # Step 6: Show statistics
            if Confirm.ask("\n[cyan]Показать статистику?[/]", default=True):
                stats = self.schedule_service.get_schedule_statistics(selected.filename)
                self.console.print()
                stats_panel = formatter.format_statistics(stats)
                self.console.print(stats_panel)

            # Step 7: Offer export
            if Confirm.ask("\n[cyan]Экспортировать график?[/]", default=False):
                self._export_schedule(schedule)

            return 0

        except KeyboardInterrupt:
            self.console.print("\n\n[yellow]Отменено пользователем[/]")
            return 130
        except Exception as e:
            self.error(f"Ошибка при загрузке графика: {e}")
            if self.settings.debug:
                raise
            return 1

    def _export_schedule(self, schedule: any) -> None:
        """
        Export schedule.

        Args:
            schedule: Schedule model
        """
        from rich.prompt import Prompt

        from schedule_dnd.domain.enums import ExportFormat
        from schedule_dnd.presentation.cli.formatters import ExportFormatter

        # Get format choice
        self.console.print("\n[bold]Форматы экспорта:[/bold]")
        self.console.print("  1. JSON")
        self.console.print("  2. Excel (XLSX)")
        self.console.print("  3. CSV")
        self.console.print("  4. Markdown")
        self.console.print("  5. HTML")
        self.console.print("  6. Все форматы")

        choice = Prompt.ask(
            "Выберите формат",
            choices=["1", "2", "3", "4", "5", "6"],
            default="6",
        )

        # Export
        if choice == "6":
            results = self.export_service.export_to_all_formats(schedule)
        else:
            format_map = {
                "1": ExportFormat.JSON,
                "2": ExportFormat.EXCEL,
                "3": ExportFormat.CSV,
                "4": ExportFormat.MARKDOWN,
                "5": ExportFormat.HTML,
            }
            fmt = format_map[choice]
            results = [self.export_service.export_schedule(schedule, fmt)]

        # Show results
        formatter = ExportFormatter(self.console)
        self.console.print()
        self.console.print(formatter.format_export_results(results))
