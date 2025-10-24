"""
Schedule business logic service.

Orchestrates schedule operations using domain models and repositories.
Author: DmitrTRC
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

from schedule_dnd.application.dto import (
    ScheduleCreateDTO,
    ScheduleListItemDTO,
    ScheduleResponseDTO,
    ScheduleStatisticsDTO,
    ShiftCreateDTO,
    UnitResponseDTO,
    UnitStatisticsDTO,
    ValidationResultDTO,
)
from schedule_dnd.domain.enums import DutyType, Month
from schedule_dnd.domain.exceptions import (
    ScheduleNotFoundError,
    UnitNotFoundError,
    ValidationError,
)
from schedule_dnd.domain.models import Schedule, ScheduleMetadata, Shift, Unit
from schedule_dnd.infrastructure.config.settings import get_settings
from schedule_dnd.infrastructure.repositories.base import ScheduleRepository


class ScheduleService:
    """Service for managing schedules."""

    def __init__(self, repository: ScheduleRepository) -> None:
        """
        Initialize schedule service.

        Args:
            repository: Repository for schedule persistence
        """
        self.repository = repository
        self.settings = get_settings()

    # ═══════════════════════════════════════════════════════════
    # Create Operations
    # ═══════════════════════════════════════════════════════════

    def create_schedule(self, dto: ScheduleCreateDTO) -> ScheduleResponseDTO:
        """
        Create a new schedule.

        Args:
            dto: Schedule creation data

        Returns:
            Created schedule as response DTO

        Raises:
            ValidationError: If validation fails
        """
        # Create metadata
        metadata = ScheduleMetadata(
            month=dto.month,
            year=dto.year,
            created_at=datetime.now(),
        )

        # Create units with shifts
        units: list[Unit] = []
        for idx, unit_dto in enumerate(dto.units, start=1):
            shifts: list[Shift] = []
            for shift_dto in unit_dto.shifts:
                shift = Shift(
                    date=shift_dto.date,
                    duty_type=shift_dto.duty_type,
                    time=shift_dto.time,
                    notes=shift_dto.notes,
                )
                shifts.append(shift)

            unit = Unit(id=idx, unit_name=unit_dto.unit_name, shifts=shifts)
            units.append(unit)

        # Create schedule
        schedule = Schedule(metadata=metadata, units=units)

        # Save schedule
        self.repository.save(schedule)

        # Convert to response DTO
        return self._schedule_to_response_dto(schedule)

    def add_shift_to_unit(
        self,
        schedule_id: str,
        unit_name: str,
        shift_dto: ShiftCreateDTO,
    ) -> ScheduleResponseDTO:
        """
        Add a shift to a specific unit in a schedule.

        Args:
            schedule_id: Schedule identifier (filename or path)
            unit_name: Name of the unit
            shift_dto: Shift data to add

        Returns:
            Updated schedule

        Raises:
            ScheduleNotFoundError: If schedule not found
            UnitNotFoundError: If unit not found
            ValidationError: If validation fails
        """
        # Load schedule
        schedule = self._load_schedule_by_id(schedule_id)

        # Find unit
        unit = schedule.get_unit_by_name(unit_name)
        if unit is None:
            raise UnitNotFoundError(unit_name)

        # Create and add shift
        shift = Shift(
            date=shift_dto.date,
            duty_type=shift_dto.duty_type,
            time=shift_dto.time,
            notes=shift_dto.notes,
        )
        unit.add_shift(shift)

        # Save updated schedule
        self.repository.save(schedule)

        return self._schedule_to_response_dto(schedule)

    # ═══════════════════════════════════════════════════════════
    # Read Operations
    # ═══════════════════════════════════════════════════════════

    def get_schedule(self, schedule_id: str) -> ScheduleResponseDTO:
        """
        Get a schedule by ID.

        Args:
            schedule_id: Schedule identifier

        Returns:
            Schedule data

        Raises:
            ScheduleNotFoundError: If schedule not found
        """
        schedule = self._load_schedule_by_id(schedule_id)
        return self._schedule_to_response_dto(schedule)

    def list_schedules(self) -> list[ScheduleListItemDTO]:
        """
        List all available schedules.

        Returns:
            List of schedule summaries
        """
        schedules = self.repository.list_schedules()
        result: list[ScheduleListItemDTO] = []

        for filepath in schedules:
            try:
                metadata = self.repository.get_schedule_metadata(filepath)
                item = ScheduleListItemDTO(
                    filename=filepath.name,
                    month=metadata.get("month", "Unknown"),
                    year=metadata.get("year", 0),
                    created_at=datetime.fromisoformat(metadata.get("created_at", "")),
                    unit_count=metadata.get("unit_count", 0),
                    total_shifts=metadata.get("total_shifts", 0),
                )
                result.append(item)
            except Exception:
                # Skip files that can't be read
                continue

        return result

    def get_unit_shifts(self, schedule_id: str, unit_name: str) -> list[Shift]:
        """
        Get all shifts for a specific unit.

        Args:
            schedule_id: Schedule identifier
            unit_name: Name of the unit

        Returns:
            List of shifts

        Raises:
            ScheduleNotFoundError: If schedule not found
            UnitNotFoundError: If unit not found
        """
        schedule = self._load_schedule_by_id(schedule_id)
        unit = schedule.get_unit_by_name(unit_name)

        if unit is None:
            raise UnitNotFoundError(unit_name)

        return unit.shifts

    # ═══════════════════════════════════════════════════════════
    # Update Operations
    # ═══════════════════════════════════════════════════════════

    def update_shift(
        self,
        schedule_id: str,
        unit_name: str,
        old_date: str,
        new_shift_dto: ShiftCreateDTO,
    ) -> ScheduleResponseDTO:
        """
        Update an existing shift.

        Args:
            schedule_id: Schedule identifier
            unit_name: Name of the unit
            old_date: Date of the shift to update
            new_shift_dto: New shift data

        Returns:
            Updated schedule

        Raises:
            ScheduleNotFoundError: If schedule not found
            UnitNotFoundError: If unit not found
            ValidationError: If shift not found
        """
        schedule = self._load_schedule_by_id(schedule_id)
        unit = schedule.get_unit_by_name(unit_name)

        if unit is None:
            raise UnitNotFoundError(unit_name)

        # Find and remove old shift
        old_shift = unit.get_shift_by_date(old_date)
        if old_shift is None:
            raise ValidationError(
                f"Shift not found for date {old_date}", field="date", value=old_date
            )

        unit.remove_shift(old_date)

        # Add new shift
        new_shift = Shift(
            date=new_shift_dto.date,
            duty_type=new_shift_dto.duty_type,
            time=new_shift_dto.time,
            notes=new_shift_dto.notes,
        )
        unit.add_shift(new_shift)

        # Save updated schedule
        self.repository.save(schedule)

        return self._schedule_to_response_dto(schedule)

    # ═══════════════════════════════════════════════════════════
    # Delete Operations
    # ═══════════════════════════════════════════════════════════

    def delete_shift(
        self, schedule_id: str, unit_name: str, date: str
    ) -> ScheduleResponseDTO:
        """
        Delete a shift from a unit.

        Args:
            schedule_id: Schedule identifier
            unit_name: Name of the unit
            date: Date of the shift to delete

        Returns:
            Updated schedule

        Raises:
            ScheduleNotFoundError: If schedule not found
            UnitNotFoundError: If unit not found
        """
        schedule = self._load_schedule_by_id(schedule_id)
        unit = schedule.get_unit_by_name(unit_name)

        if unit is None:
            raise UnitNotFoundError(unit_name)

        unit.remove_shift(date)

        # Save updated schedule
        self.repository.save(schedule)

        return self._schedule_to_response_dto(schedule)

    def delete_schedule(self, schedule_id: str) -> bool:
        """
        Delete a schedule.

        Args:
            schedule_id: Schedule identifier

        Returns:
            True if deletion was successful

        Raises:
            ScheduleNotFoundError: If schedule not found
        """
        filepath = self._resolve_schedule_path(schedule_id)
        return self.repository.delete(filepath)

    # ═══════════════════════════════════════════════════════════
    # Validation Operations
    # ═══════════════════════════════════════════════════════════

    def validate_schedule(self, dto: ScheduleCreateDTO) -> ValidationResultDTO:
        """
        Validate a schedule before creation.

        Args:
            dto: Schedule data to validate

        Returns:
            Validation result with any errors or warnings
        """
        errors: list[str] = []
        warnings: list[str] = []

        # Validate each unit
        for unit_dto in dto.units:
            # Check for duplicate shifts
            seen_dates: set[str] = set()
            for shift_dto in unit_dto.shifts:
                if shift_dto.date in seen_dates:
                    errors.append(
                        f"Duplicate shift for {unit_dto.unit_name} on {shift_dto.date}"
                    )
                seen_dates.add(shift_dto.date)

            # Warn if no shifts
            if not unit_dto.shifts:
                warnings.append(f"No shifts defined for {unit_dto.unit_name}")

        # Check if schedule already exists
        month_num = dto.month.to_number()
        filepath = self.settings.get_schedule_file_path(dto.year, month_num)
        if self.repository.exists(filepath):
            warnings.append(
                f"Schedule for {dto.month.display_name()} {dto.year} already exists and will be overwritten"
            )

        return ValidationResultDTO(
            is_valid=len(errors) == 0, errors=errors, warnings=warnings
        )

    # ═══════════════════════════════════════════════════════════
    # Statistics Operations
    # ═══════════════════════════════════════════════════════════

    def get_schedule_statistics(self, schedule_id: str) -> ScheduleStatisticsDTO:
        """
        Get statistics for a schedule.

        Args:
            schedule_id: Schedule identifier

        Returns:
            Schedule statistics

        Raises:
            ScheduleNotFoundError: If schedule not found
        """
        schedule = self._load_schedule_by_id(schedule_id)

        # Calculate overall statistics
        total_shifts = schedule.get_total_shifts()
        shifts_by_type = schedule.get_shifts_by_type()

        # Calculate unit statistics
        unit_stats: list[UnitStatisticsDTO] = []
        for unit in schedule.units:
            stats = UnitStatisticsDTO(
                unit_name=unit.unit_name,
                total_shifts=unit.get_shift_count(),
                shifts_by_type=unit.get_shifts_by_type(),
                avg_shifts_per_week=unit.get_shift_count() / 4.0,  # Approximate
            )
            unit_stats.append(stats)

        return ScheduleStatisticsDTO(
            month=schedule.metadata.month.display_name(),
            year=schedule.metadata.year,
            total_units=len(schedule.units),
            total_shifts=total_shifts,
            shifts_by_type=shifts_by_type,
            units=unit_stats,
        )

    # ═══════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════

    def _load_schedule_by_id(self, schedule_id: str) -> Schedule:
        """Load a schedule by ID (filename or path)."""
        filepath = self._resolve_schedule_path(schedule_id)

        if not self.repository.exists(filepath):
            raise ScheduleNotFoundError(schedule_id)

        return self.repository.load(filepath)

    def _resolve_schedule_path(self, schedule_id: str) -> Path:
        """Resolve schedule ID to full path."""
        # If it's already a path, use it
        if "/" in schedule_id or "\\" in schedule_id:
            return Path(schedule_id)

        # If it's just a filename, look in data directory
        if schedule_id.endswith(".json"):
            return self.settings.data_dir / schedule_id

        # If it's year_month format, construct filename
        if "_" in schedule_id:
            return self.settings.data_dir / f"schedule_{schedule_id}.json"

        # Default: treat as filename
        return self.settings.data_dir / schedule_id

    def _schedule_to_response_dto(self, schedule: Schedule) -> ScheduleResponseDTO:
        """Convert Schedule model to response DTO."""
        from schedule_dnd.application.dto import ScheduleMetadataDTO, ShiftResponseDTO

        # Convert metadata
        metadata_dto = ScheduleMetadataDTO(
            month=schedule.metadata.month.display_name(),
            year=schedule.metadata.year,
            created_at=schedule.metadata.created_at,
            created_by=schedule.metadata.created_by,
            source=schedule.metadata.source,
            signatory=schedule.metadata.signatory,
            note=schedule.metadata.note,
        )

        # Convert units
        unit_dtos: list[UnitResponseDTO] = []
        for unit in schedule.units:
            shift_dtos = [
                ShiftResponseDTO(
                    date=shift.date,
                    duty_type=shift.duty_type,
                    time=shift.time,
                    notes=shift.notes,
                )
                for shift in unit.shifts
            ]

            unit_dto = UnitResponseDTO(
                id=unit.id, unit_name=unit.unit_name, shifts=shift_dtos
            )
            unit_dtos.append(unit_dto)

        return ScheduleResponseDTO(metadata=metadata_dto, schedule=unit_dtos)
