"""
Create command - interactive schedule creation.

Author: DmitrTRC
Version: 2.0 (No Cyrillic Input + Autosave)
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.prompt import Confirm, IntPrompt

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
    """Command for creating new schedules with autosave."""

    AUTOSAVE_FILE = Path("/tmp/schedule_dnd_autosave.json")

    def execute(self) -> int:
        """
        Execute create command.

        Returns:
            Exit code
        """
        logger.info("=" * 50)
        logger.info("Starting CreateCommand execution (v2.0 - No Cyrillic)")
        self.console.print("\n[bold cyan]📝 Создание нового графика[/bold cyan]\n")

        try:
            # Check for autosave
            autosave_data = self._check_autosave()

            if autosave_data:
                month = Month.from_number(autosave_data["month"])
                year = autosave_data["year"]
                units_dto = self._restore_units(autosave_data["units"])
                start_from = autosave_data.get("last_unit_index", 0)

                self.console.print(
                    f"[green]✓ Восстановлено: {month.display_name()} {year}[/green]"
                )
                self.console.print(
                    f"[yellow]Уже добавлено юнитов: {len(units_dto)}[/yellow]\n"
                )
            else:
                # Step 1: Input month and year (NO CYRILLIC!)
                logger.info("Step 1: Inputting period (month/year) - using numbers")
                month, year = self._input_period()
                logger.info(f"Period selected: {month.display_name()} {year}")

                units_dto: list[UnitCreateDTO] = []
                start_from = 0

            # Step 2: Create units with shifts
            logger.info(f"Step 2: Starting input for {len(UNITS)} units")

            for idx in range(start_from, len(UNITS)):
                unit_name = UNITS[idx]
                unit_number = idx + 1

                self.console.print()
                formatter = ScheduleFormatter(self.console)
                self.console.print(formatter.format_unit_header(unit_number, unit_name))

                logger.info(f"[Unit {unit_number}/8] Inputting shifts for: {unit_name}")

                # Input shifts for this unit
                shifts_dto = self._input_shifts_for_unit(unit_name, month, year)

                if shifts_dto:
                    units_dto.append(
                        UnitCreateDTO(unit_name=unit_name, shifts=shifts_dto)
                    )
                    logger.info(
                        f"[Unit {unit_number}/8] Added {len(shifts_dto)} shifts"
                    )

                    # AUTOSAVE after each unit!
                    self._autosave(month, year, units_dto, idx)
                    self.console.print(
                        f"[dim]💾 Автосохранение: {unit_number}/8 юнитов[/dim]"
                    )
                else:
                    logger.warning(f"[Unit {unit_number}/8] No shifts added")

                # Ask if want to continue
                if unit_number < len(UNITS):
                    if not Confirm.ask("\n[yellow]Продолжить?[/]", default=True):
                        logger.info(f"User chose to stop after unit {unit_number}")
                        self.console.print(
                            "\n[yellow]ℹ️ Прогресс сохранен. "
                            "Запустите команду снова для продолжения.[/yellow]"
                        )
                        return 0

            if not units_dto:
                logger.warning("No shifts added across all units, canceling")
                self.error("Не добавлено ни одной смены. Отмена создания графика.")
                self._clear_autosave()
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
                self.console.print(
                    "\n[yellow]💾 Данные сохранены. "
                    "Исправьте ошибки и запустите снова.[/yellow]"
                )
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
                f"Schedule SAVED: {response.metadata.month} {response.metadata.year}"
            )

            # Clear autosave after successful save
            self._clear_autosave()

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
            self.console.print(
                "\n\n[yellow]💾 Прогресс сохранен. "
                "Запустите команду снова для продолжения.[/yellow]"
            )
            return 130
        except Exception as e:
            logger.exception(f"CRITICAL ERROR in CreateCommand: {e}")
            self.error(f"Ошибка при создании графика: {e}")
            self.console.print("\n[yellow]💾 Попытка сохранения данных...[/yellow]")
            if self.settings.debug:
                raise
            return 1

    def _input_period(self) -> tuple[Month, int]:
        """
        Input month and year using NUMBERS only (NO CYRILLIC).

        Returns:
            Tuple of (Month, year)
        """
        self.console.print("[bold]Введите период:[/bold]\n")

        # Get defaults
        now = datetime.now()
        default_month = now.month
        default_year = now.year

        # Input month as NUMBER (1-12)
        while True:
            try:
                self.console.print("Месяц:")
                self.console.print("  1=Январь   2=Февраль   3=Март      4=Апрель")
                self.console.print("  5=Май      6=Июнь      7=Июль      8=Август")
                self.console.print("  9=Сентябрь 10=Октябрь  11=Ноябрь   12=Декабрь\n")

                month_num = IntPrompt.ask(
                    f"Введите номер месяца [1-12]",
                    default=default_month,
                )

                if not 1 <= month_num <= 12:
                    self.error("Номер месяца должен быть от 1 до 12")
                    continue

                month = Month.from_number(month_num)
                logger.debug(f"Month selected: {month_num} → {month.display_name()}")
                break

            except ValueError as e:
                logger.error(f"Invalid month input: {e}")
                self.error(f"Неверный ввод: {e}")
                continue
            except KeyboardInterrupt:
                raise

        # Input year
        while True:
            try:
                year = IntPrompt.ask(
                    f"Год [{default_year}-{default_year + 5}]",
                    default=default_year,
                )

                if year < default_year or year > default_year + 5:
                    self.error(
                        f"Год должен быть между {default_year} и {default_year + 5}"
                    )
                    continue

                logger.debug(f"Year input: {year}")
                break

            except ValueError as e:
                logger.error(f"Invalid year input: {e}")
                self.error(f"Неверный ввод: {e}")
                continue
            except KeyboardInterrupt:
                raise

        self.console.print(f"\n[green]✓ Период: {month.display_name()} {year}[/green]")
        return month, year

    def _input_shifts_for_unit(
        self, unit_name: str, month: Month, year: int
    ) -> list[ShiftCreateDTO]:
        """
        Input shifts for a unit with error recovery.

        Args:
            unit_name: Name of the unit
            month: Month
            year: Year

        Returns:
            List of shift DTOs
        """
        shifts_dto: list[ShiftCreateDTO] = []
        seen_dates: set[str] = set()

        self.console.print(f"\n[dim]Вводите день (1-31) и тип дежурства (1/2/3).[/]")
        self.console.print(f"[dim]Оставьте пустым или введите 'q' для завершения.[/]\n")

        formatter = ScheduleFormatter(self.console)
        shift_count = 0

        while True:
            try:
                # Input day - empty to finish
                day_input = input(f"День (1-31) или Enter: ").strip()

                logger.debug(f"[Shift #{shift_count + 1}] Raw input: '{day_input}'")

                # Check if user wants to finish
                if not day_input or day_input.lower() in [
                    "q",
                    "quit",
                    "done",
                    "готово",
                ]:
                    logger.info(f"User finished {unit_name}: {len(shifts_dto)} shifts")
                    break

                # Parse day
                try:
                    day = int(day_input)
                except ValueError:
                    logger.warning(f"Invalid day input: '{day_input}'")
                    self.error(f"Неверный день: '{day_input}'. Введите число 1-31")
                    continue

                if not 1 <= day <= 31:
                    logger.warning(f"Day {day} out of range")
                    self.error("День должен быть от 1 до 31")
                    continue

                # Format date
                date_str = f"{day:02d}.{month.to_number():02d}.{year}"
                logger.debug(f"Formatted date: {date_str}")

                # Check duplicate
                if date_str in seen_dates:
                    logger.warning(f"Duplicate date: {date_str}")
                    self.error(f"Смена на {date_str} уже добавлена")
                    continue

                # Input duty type using NUMBERS (NO CYRILLIC!)
                self.console.print("\nТип дежурства:")
                self.console.print(
                    "  1. ПДН (Подразделение по делам несовершеннолетних)"
                )
                self.console.print("  2. ППСП (Патрульно-постовая служба)")
                self.console.print("  3. УУП (Участковые уполномоченные)")

                choice = input("Выбор [1/2/3] (3): ").strip()

                # Map number to duty type
                if not choice or choice == "3":
                    duty_type = DutyType.UUP
                elif choice == "1":
                    duty_type = DutyType.PDN
                elif choice == "2":
                    duty_type = DutyType.PPSP
                else:
                    logger.error(f"Invalid choice '{choice}'")
                    self.error(f"Неверный выбор: {choice}. Введите 1, 2 или 3")
                    continue

                logger.debug(f"Duty type selected: {duty_type.value}")

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

            except KeyboardInterrupt:
                self.console.print(
                    "\n[yellow]Прервано. Сохраняем текущий прогресс...[/yellow]"
                )
                break
            except Exception as e:
                logger.error(f"Error during shift input: {e}")
                self.error(f"Ошибка: {e}. Попробуйте еще раз.")
                continue

        if shifts_dto:
            logger.info(f"Completed {unit_name}: {len(shifts_dto)} shifts")
            self.console.print(f"\n[green]✓ Добавлено смен: {len(shifts_dto)}[/green]")
        else:
            logger.warning(f"Completed {unit_name}: NO shifts")
            self.console.print(f"\n[yellow]Смены не добавлены[/yellow]")

        return shifts_dto

    def _autosave(
        self, month: Month, year: int, units: list[UnitCreateDTO], last_unit_index: int
    ) -> None:
        """
        Autosave current progress.

        Args:
            month: Current month
            year: Current year
            units: List of units with shifts
            last_unit_index: Index of last completed unit
        """
        try:
            data = {
                "month": month.to_number(),
                "year": year,
                "last_unit_index": last_unit_index + 1,  # Next unit to start
                "units": [
                    {
                        "unit_name": u.unit_name,
                        "shifts": [
                            {"date": s.date, "duty_type": s.duty_type.value}
                            for s in u.shifts
                        ],
                    }
                    for u in units
                ],
                "timestamp": datetime.now().isoformat(),
            }

            with open(self.AUTOSAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"Autosaved: {len(units)} units to {self.AUTOSAVE_FILE}")

        except Exception as e:
            logger.error(f"Autosave failed: {e}")

    def _check_autosave(self) -> Optional[dict]:
        """
        Check if autosave exists.

        Returns:
            Autosave data or None
        """
        if not self.AUTOSAVE_FILE.exists():
            return None

        try:
            with open(self.AUTOSAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            timestamp = data.get("timestamp", "неизвестно")
            self.console.print(
                f"\n[cyan]🔍 Найдено автосохранение от {timestamp}[/cyan]"
            )

            if Confirm.ask("[yellow]Восстановить прогресс?[/]", default=True):
                logger.info("User chose to restore autosave")
                return data
            else:
                logger.info("User chose to start fresh")
                self._clear_autosave()
                return None

        except Exception as e:
            logger.error(f"Failed to load autosave: {e}")
            self._clear_autosave()
            return None

    def _restore_units(self, units_data: list[dict]) -> list[UnitCreateDTO]:
        """
        Restore units from autosave data.

        Args:
            units_data: List of unit dicts

        Returns:
            List of UnitCreateDTO
        """
        units = []
        for unit_data in units_data:
            shifts = [
                ShiftCreateDTO(date=s["date"], duty_type=DutyType(s["duty_type"]))
                for s in unit_data["shifts"]
            ]
            units.append(UnitCreateDTO(unit_name=unit_data["unit_name"], shifts=shifts))
        return units

    def _clear_autosave(self) -> None:
        """Clear autosave file."""
        try:
            if self.AUTOSAVE_FILE.exists():
                self.AUTOSAVE_FILE.unlink()
                logger.info("Autosave cleared")
        except Exception as e:
            logger.error(f"Failed to clear autosave: {e}")

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

        choice = input("Выберите формат [1-6] (6): ").strip() or "6"

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
            fmt = format_map.get(choice, ExportFormat.JSON)
            logger.info(f"Exporting to: {fmt.value}")
            results = [self.export_service.export_schedule(schedule, fmt)]

        # Show results
        from schedule_dnd.presentation.cli.formatters import ExportFormatter

        formatter = ExportFormatter(self.console)
        self.console.print()
        self.console.print(formatter.format_export_results(results))

        success_count = len([r for r in results if r.success])
        logger.info(f"Export complete: {success_count}/{len(results)} successful")
