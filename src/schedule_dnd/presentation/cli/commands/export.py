"""
Export command - export schedules to various formats.

Author: DmitrTRC
"""

from rich.prompt import IntPrompt, Prompt

from schedule_dnd.domain.enums import ExportFormat
from schedule_dnd.presentation.cli.commands.base import BaseCommand
from schedule_dnd.presentation.cli.formatters import ExportFormatter, ScheduleFormatter


class ExportCommand(BaseCommand):
    """Command for exporting schedules."""

    def execute(self) -> int:
        """
        Execute export command.

        Returns:
            Exit code
        """
        self.console.print("\n[bold cyan]Экспорт графика[/bold cyan]\n")

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
                "\nВыберите график для экспорта (номер)",
                default=1,
            )

            if not 1 <= choice <= len(schedules):
                self.error(f"Неверный номер: {choice}")
                return 1

            selected = schedules[choice - 1]

            # Step 4: Load schedule
            self.console.print(f"\n[dim]Загрузка {selected.filename}...[/dim]")

            filepath = self.settings.data_dir / selected.filename
            schedule = self.repository.load(filepath)

            # Step 5: Select export format
            self.console.print("\n[bold]Форматы экспорта:[/bold]")
            self.console.print("  1. JSON - структурированный формат")
            self.console.print("  2. Excel (XLSX) - таблица с форматированием")
            self.console.print("  3. CSV - универсальный табличный формат")
            self.console.print("  4. Markdown - читаемые таблицы")
            self.console.print("  5. HTML - веб-страница с дизайном")
            self.console.print("  6. Все форматы сразу")

            format_choice = Prompt.ask(
                "\nВыберите формат",
                choices=["1", "2", "3", "4", "5", "6"],
                default="6",
            )

            # Step 6: Export
            self.console.print("\n[dim]Экспорт...[/dim]")

            if format_choice == "6":
                results = self.export_service.export_to_all_formats(schedule)
            else:
                format_map = {
                    "1": ExportFormat.JSON,
                    "2": ExportFormat.EXCEL,
                    "3": ExportFormat.CSV,
                    "4": ExportFormat.MARKDOWN,
                    "5": ExportFormat.HTML,
                }
                fmt = format_map[format_choice]
                results = [self.export_service.export_schedule(schedule, fmt)]

            # Step 7: Show results
            export_formatter = ExportFormatter(self.console)
            self.console.print()
            self.console.print(export_formatter.format_export_results(results))

            # Success summary
            success_count = sum(1 for r in results if r.success)
            if success_count > 0:
                self.console.print()
                self.success(f"Успешно экспортировано: {success_count}/{len(results)}")
                self.console.print(
                    f"\n[dim]Файлы сохранены в: {self.settings.output_dir}[/dim]"
                )

            return 0 if success_count > 0 else 1

        except KeyboardInterrupt:
            self.console.print("\n\n[yellow]Отменено пользователем[/]")
            return 130
        except Exception as e:
            self.error(f"Ошибка при экспорте: {e}")
            if self.settings.debug:
                raise
            return 1
