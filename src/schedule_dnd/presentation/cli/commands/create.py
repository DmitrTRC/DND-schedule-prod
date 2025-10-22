"""
Create command - interactive schedule creation.

Author: DmitrTRC
"""

from datetime import datetime

from rich.prompt import Confirm, IntPrompt, Prompt

from schedule_dnd.application.dto import (
    ScheduleCreateDTO,
    ShiftCreateDTO,
    UnitCreateDTO,
)
from schedule_dnd.domain.constants import UNITS
from schedule_dnd.domain.enums import DutyType, Month
from schedule_dnd.domain.exceptions import DuplicateShiftError, ValidationError
from schedule_dnd.presentation.cli.commands.base import BaseCommand
from schedule_dnd.presentation.cli.formatters import ScheduleFormatter


class CreateCommand(BaseCommand):
    """Command for creating new schedules."""

    def execute(self) -> int:
        """
        Execute create command.

        Returns:
            Exit code
        """
        self.console.print("\n[bold cyan]Создание нового графика[/bold cyan]\n")

        try:
            # Step 1: Input month and year
            month, year = self._input_period()

            # Step 2: Create units with shifts
            units_dto: list[UnitCreateDTO] = []

            for idx, unit_name in enumerate(UNITS, 1):
                self.console.print()
                formatter = ScheduleFormatter(self.console)
                self.console.print(formatter.format_unit_header(idx, unit_name))

                # Input shifts for this unit
                shifts_dto = self._input_shifts_for_unit(unit_name, month, year)

                if shifts_dto:
                    units_dto.append(
                        UnitCreateDTO(unit_name=unit_name, shifts=shifts_dto)
                    )

                # Ask if want to continue
                if idx < len(UNITS):
                    if not Confirm.ask("\n[yellow]Продолжить?[/]", default=True):
                        break

            if not units_dto:
                self.error("Не добавлено ни одной смены. Отмена создания графика.")
                return 1

            # Step 3: Create schedule
            schedule_dto = ScheduleCreateDTO(month=month, year=year, units=units_dto)

            # Step 4: Validate
            validation_result = self.schedule_service.validate_schedule(schedule_dto)

            if not validation_result.is_valid:
                self.error("Ошибки валидации:")
                for error in validation_result.errors:
                    self.console.print(f"  - {error}")
                return 1

            if validation_result.warnings:
                self.warning("Предупреждения:")
                for warning in validation_result.warnings:
                    self.console.print(f"  - {warning}")

                if not Confirm.ask("\n[yellow]Продолжить?[/]", default=True):
                    return 0

            # Step 5: Save
            response = self.schedule_service.create_schedule(schedule_dto)
            self.success(
                f"График создан: {response.metadata.month} {response.metadata.year}"
            )

            # Step 6: Offer export
            if Confirm.ask("\n[cyan]Экспортировать график?[/]", default=True):
                self._export_schedule(response)

            return 0

        except KeyboardInterrupt:
            self.console.print("\n\n[yellow]Отменено пользователем[/]")
            return 130
        except Exception as e:
            self.error(f"Ошибка при создании графика: {e}")
            if self.settings.debug:
                raise
            return 1

    def _input_period(self) -> tuple[Month, int]:
        """
        Input month and year.

        Returns:
            Tuple of (Month, year)
        """
        # Input month
        self.console.print("[bold]Введите период:[/bold]")
        month_name = (
            Prompt.ask(
                "Месяц (например: октябрь, ноябрь)",
                default="октябрь",
            )
            .lower()
            .strip()
        )

        try:
            month = Month.from_string(month_name)
        except ValueError:
            self.error(f"Неверный месяц: {month_name}")
            raise

        # Input year
        current_year = datetime.now().year
        year = IntPrompt.ask(
            "Год",
            default=current_year,
        )

        if year < current_year or year > current_year + 5:
            self.error(f"Год должен быть между {current_year} и {current_year + 5}")
            raise ValueError("Invalid year")

        self.console.print(f"\n[green]✓ Период: {month.display_name()} {year}[/green]")

        return month, year

    def _input_shifts_for_unit(
        self, unit_name: str, month: Month, year: int
    ) -> list[ShiftCreateDTO]:
        """
        Input shifts for a unit.

        Args:
            unit_name: Name of the unit
            month: Month
            year: Year

        Returns:
            List of shift DTOs
        """
        shifts_dto: list[ShiftCreateDTO] = []
        seen_dates: set[str] = set()

        self.console.print(f"\n[dim]Вводите день (число 1-31) и тип дежурства.[/]")
        self.console.print(f"[dim]Введите 'готово' когда закончите.[/]\n")

        formatter = ScheduleFormatter(self.console)

        while True:
            # Input day
            day_input = (
                Prompt.ask(
                    f"День или 'готово'",
                    default="готово",
                )
                .strip()
                .lower()
            )

            if day_input in ["готово", "done", "q", "quit"]:
                break

            # Parse day
            try:
                day = int(day_input)
                if not 1 <= day <= 31:
                    self.error("День должен быть от 1 до 31")
                    continue

                # Format date
                date_str = f"{day:02d}.{month.value:02d}.{year}"

                # Check duplicate
                if date_str in seen_dates:
                    self.error(f"Смена на {date_str} уже добавлена")
                    continue

            except ValueError:
                self.error(f"Неверный день: {day_input}")
                continue

            # Input duty type
            duty_type_input = (
                Prompt.ask(
                    "Тип дежурства",
                    choices=["ПДН", "ППСП", "УУП"],
                    default="УУП",
                )
                .upper()
                .strip()
            )

            try:
                duty_type = DutyType(duty_type_input)

                # Create shift DTO
                shift_dto = ShiftCreateDTO(
                    date=date_str,
                    duty_type=duty_type,
                )

                shifts_dto.append(shift_dto)
                seen_dates.add(date_str)

                # Show confirmation
                self.console.print(
                    formatter.format_shift_added(date_str, duty_type.value)
                )

            except ValueError as e:
                self.error(f"Неверный тип дежурства: {duty_type_input}")
                continue

        if shifts_dto:
            self.console.print(f"\n[green]✓ Добавлено смен: {len(shifts_dto)}[/green]")
        else:
            self.console.print(f"\n[yellow]Смены не добавлены[/yellow]")

        return shifts_dto

    def _export_schedule(self, response: any) -> None:
        """
        Export schedule.

        Args:
            response: Schedule response DTO
        """
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

        # Load schedule for export
        from schedule_dnd.domain.enums import ExportFormat

        filename = f"schedule_{response.metadata.year}_{response.metadata.month.value:02d}.json"
        filepath = self.settings.data_dir / filename

        schedule = self.repository.load(filepath)

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
        from schedule_dnd.presentation.cli.formatters import ExportFormatter

        formatter = ExportFormatter(self.console)
        self.console.print()
        self.console.print(formatter.format_export_results(results))
