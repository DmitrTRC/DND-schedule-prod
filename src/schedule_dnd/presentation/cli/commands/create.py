"""
Create command - interactive schedule creation.

Author: DmitrTRC
"""

import logging
from datetime import datetime

from rich.prompt import Confirm, IntPrompt, Prompt

from schedule_dnd.application.dto import (
    ScheduleCreateDTO,
    ShiftCreateDTO,
    UnitCreateDTO,
)
from schedule_dnd.domain.constants import UNITS
from schedule_dnd.domain.enums import DutyType, Month
from schedule_dnd.presentation.cli.commands.base import BaseCommand
from schedule_dnd.presentation.cli.formatters import ScheduleFormatter

logger = logging.getLogger(__name__)


class CreateCommand(BaseCommand):
    """Command for creating new schedules."""

    def execute(self) -> int:
        """
        Execute create command.

        Returns:
            Exit code
        """
        logger.info("=" * 50)
        logger.info("Starting CreateCommand execution")
        self.console.print("\n[bold cyan]Создание нового графика[/bold cyan]\n")

        try:
            # Step 1: Input month and year
            logger.info("Step 1: Inputting period (month/year)")
            month, year = self._input_period()
            logger.info(f"Period selected: {month.display_name()} {year}")

            # Step 2: Create units with shifts
            units_dto: list[UnitCreateDTO] = []
            logger.info(f"Step 2: Starting input for {len(UNITS)} units")

            for idx, unit_name in enumerate(UNITS, 1):
                self.console.print()
                formatter = ScheduleFormatter(self.console)
                self.console.print(formatter.format_unit_header(idx, unit_name))

                logger.info(f"[Unit {idx}/8] Inputting shifts for: {unit_name}")

                # Input shifts for this unit
                shifts_dto = self._input_shifts_for_unit(unit_name, month, year)

                if shifts_dto:
                    units_dto.append(
                        UnitCreateDTO(unit_name=unit_name, shifts=shifts_dto)
                    )
                    logger.info(
                        f"[Unit {idx}/8] Added {len(shifts_dto)} shifts for {unit_name}"
                    )
                else:
                    logger.warning(f"[Unit {idx}/8] No shifts added for {unit_name}")

                # Ask if want to continue
                if idx < len(UNITS):
                    if not Confirm.ask("\n[yellow]Продолжить?[/]", default=True):
                        logger.info(f"User chose to stop after unit {idx}")
                        break

            if not units_dto:
                logger.warning("No shifts added across all units, canceling")
                self.error("Не добавлено ни одной смены. Отмена создания графика.")
                return 1

            # Step 3: Create schedule
            logger.info(f"Step 3: Creating schedule DTO with {len(units_dto)} units")
            schedule_dto = ScheduleCreateDTO(month=month, year=year, units=units_dto)

            # Step 4: Validate
            logger.info("Step 4: Validating schedule")
            validation_result = self.schedule_service.validate_schedule(schedule_dto)

            if not validation_result.is_valid:
                logger.error(f"Validation FAILED: {validation_result.errors}")
                self.error("Ошибки валидации:")
                for error in validation_result.errors:
                    self.console.print(f"  - {error}")
                return 1

            if validation_result.warnings:
                logger.warning(f"Validation warnings: {validation_result.warnings}")
                self.warning("Предупреждения:")
                for warning in validation_result.warnings:
                    self.console.print(f"  - {warning}")

                if not Confirm.ask("\n[yellow]Продолжить?[/]", default=True):
                    logger.info("User cancelled after validation warnings")
                    return 0
            else:
                logger.info("Validation PASSED")

            # Step 5: Save
            logger.info("Step 5: Saving schedule")
            response = self.schedule_service.create_schedule(schedule_dto)
            logger.info(
                f"Schedule SAVED successfully: {response.metadata.month} {response.metadata.year}"
            )
            self.success(
                f"График создан: {response.metadata.month} {response.metadata.year}"
            )

            # Step 6: Offer export
            if Confirm.ask("\n[cyan]Экспортировать график?[/]", default=True):
                logger.info("Step 6: User chose to export")
                self._export_schedule(response)
            else:
                logger.info("User skipped export")

            logger.info("CreateCommand execution completed successfully")
            return 0

        except KeyboardInterrupt:
            logger.info("User interrupted with Ctrl+C")
            self.console.print("\n\n[yellow]Отменено пользователем[/]")
            return 130
        except Exception as e:
            logger.exception(f"CRITICAL ERROR in CreateCommand: {e}")
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

        logger.debug(f"Month input: '{month_name}'")

        try:
            month = Month.from_string(month_name)
            logger.debug(f"Month parsed successfully: {month}")
        except ValueError as e:
            logger.error(f"Invalid month input: '{month_name}' - {e}")
            self.error(f"Неверный месяц: {month_name}")
            raise

        # Input year
        current_year = datetime.now().year
        year = IntPrompt.ask(
            "Год",
            default=current_year,
        )

        logger.debug(f"Year input: {year}")

        if year < current_year or year > current_year + 5:
            logger.error(f"Year out of valid range: {year}")
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
        shift_count = 0

        while True:
            # Input day - NO DEFAULT to avoid conflicts!
            day_input = Prompt.ask(f"День (1-31) или 'готово'").strip()

            logger.debug(f"[Shift #{shift_count + 1}] Raw input: '{day_input}'")

            # Check if user wants to finish
            if day_input.lower() in ["готово", "done", "q", "quit", ""]:
                logger.info(
                    f"User finished {unit_name}: added {len(shifts_dto)} shifts total"
                )
                break

            # Parse day
            try:
                day = int(day_input)
                logger.debug(f"[Shift #{shift_count + 1}] Parsed as day: {day}")

                if not 1 <= day <= 31:
                    logger.warning(
                        f"[Shift #{shift_count + 1}] Day {day} out of range [1-31]"
                    )
                    self.error("День должен быть от 1 до 31")
                    continue

                # Format date
                date_str = f"{day:02d}.{month.to_number():02d}.{year}"
                logger.debug(f"[Shift #{shift_count + 1}] Formatted date: {date_str}")

                # Check duplicate
                if date_str in seen_dates:
                    logger.warning(f"[Shift #{shift_count + 1}] Duplicate: {date_str}")
                    self.error(f"Смена на {date_str} уже добавлена")
                    continue

            except ValueError as e:
                logger.error(
                    f"[Shift #{shift_count + 1}] Parse error for '{day_input}': {e}"
                )
                self.error(
                    f"Неверный день: '{day_input}'. Введите число от 1 до 31 или 'готово'"
                )
                continue

            # Input duty type - use numbers to avoid encoding issues completely
            self.console.print("\nТип дежурства:")
            self.console.print("  1. ПДН (Подразделение по делам несовершеннолетних)")
            self.console.print("  2. ППСП (Патрульно-постовая служба)")
            self.console.print("  3. УУП (Участковые уполномоченные)")
            self.console.print("Выбор [1/2/3] (3): ", end="")

            try:
                choice = input().strip()
            except UnicodeDecodeError:
                # Fallback for encoding issues
                import sys

                raw_input = sys.stdin.buffer.readline()
                choice = raw_input.decode("utf-8", errors="ignore").strip()

            # Map number to duty type
            if not choice or choice == "3":
                duty_type_input = "УУП"
            elif choice == "1":
                duty_type_input = "ПДН"
            elif choice == "2":
                duty_type_input = "ППСП"
            else:
                logger.error(f"[Shift #{shift_count + 1}] Invalid choice '{choice}'")
                self.error(f"Неверный выбор: {choice}. Введите 1, 2 или 3")
                continue

            logger.debug(f"[Shift #{shift_count + 1}] Duty type: '{duty_type_input}'")

            try:
                duty_type = DutyType(duty_type_input)

                # Create shift DTO
                shift_dto = ShiftCreateDTO(
                    date=date_str,
                    duty_type=duty_type,
                )

                shifts_dto.append(shift_dto)
                seen_dates.add(date_str)
                shift_count += 1

                logger.info(
                    f"[Shift #{shift_count}] SUCCESS: {date_str} - {duty_type.value}"
                )

                # Show confirmation
                self.console.print(
                    formatter.format_shift_added(date_str, duty_type.value)
                )

            except ValueError as e:
                logger.error(
                    f"[Shift #{shift_count + 1}] Invalid duty type '{duty_type_input}': {e}"
                )
                self.error(f"Неверный тип дежурства: {duty_type_input}")
                continue

        if shifts_dto:
            logger.info(f"Completed {unit_name}: {len(shifts_dto)} shifts")
            self.console.print(f"\n[green]✓ Добавлено смен: {len(shifts_dto)}[/green]")
        else:
            logger.warning(f"Completed {unit_name}: NO shifts")
            self.console.print(f"\n[yellow]Смены не добавлены[/yellow]")

        return shifts_dto

    def _export_schedule(self, response: any) -> None:
        """
        Export schedule.

        Args:
            response: Schedule response DTO
        """
        logger.info("Starting export workflow")

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

        logger.info(f"Export format choice: {choice}")

        # Load schedule for export
        from schedule_dnd.domain.enums import ExportFormat

        filename = f"schedule_{response.metadata.year}_{response.metadata.month.to_number():02d}.json"
        filepath = self.settings.data_dir / filename

        logger.debug(f"Loading schedule from: {filepath}")
        schedule = self.repository.load(filepath)
        logger.debug("Schedule loaded")

        # Export
        if choice == "6":
            logger.info("Exporting to ALL formats")
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
            logger.info(f"Exporting to: {fmt.value}")
            results = [self.export_service.export_schedule(schedule, fmt)]

        # Show results
        from schedule_dnd.presentation.cli.formatters import ExportFormatter

        formatter = ExportFormatter(self.console)
        self.console.print()
        self.console.print(formatter.format_export_results(results))

        success_count = len([r for r in results if r.success])
        logger.info(f"Export complete: {success_count}/{len(results)} successful")
