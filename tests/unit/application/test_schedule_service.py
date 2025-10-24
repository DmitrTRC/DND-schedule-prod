"""
Unit tests for ScheduleService.

Comprehensive testing of schedule business logic operations.
Author: DmitrTRC
"""

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from pydantic import ValidationError

from schedule_dnd.application.dto import (
    ScheduleCreateDTO,
    ScheduleListItemDTO,
    ScheduleResponseDTO,
    ScheduleStatisticsDTO,
    ShiftCreateDTO,
    UnitCreateDTO,
    ValidationResultDTO,
)
from schedule_dnd.application.services.schedule_service import ScheduleService
from schedule_dnd.domain.enums import DutyType, Month
from schedule_dnd.domain.exceptions import ScheduleNotFoundError, UnitNotFoundError
from schedule_dnd.domain.exceptions import ValidationError as DomainValidationError
from schedule_dnd.domain.models import Schedule, ScheduleMetadata, Shift, Unit
from schedule_dnd.infrastructure.repositories.base import ScheduleRepository

# ═══════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def mock_repository() -> Mock:
    """Create a mock repository."""
    repo = MagicMock(spec=ScheduleRepository)
    repo.save = Mock()
    repo.load = Mock()
    repo.exists = Mock(return_value=True)
    repo.delete = Mock(return_value=True)
    repo.list_schedules = Mock(return_value=[])
    repo.get_schedule_metadata = Mock(return_value={})
    return repo


@pytest.fixture
def schedule_service(mock_repository: Mock) -> ScheduleService:
    """Create a ScheduleService instance with mocked repository."""
    return ScheduleService(repository=mock_repository)


@pytest.fixture
def sample_shift_dto() -> ShiftCreateDTO:
    """Create a sample shift DTO."""
    return ShiftCreateDTO(
        date="07.10.2025",
        duty_type=DutyType.UUP,
        time="18:00-22:00",
        notes="Test shift",
    )


@pytest.fixture
def sample_unit_dto(sample_shift_dto: ShiftCreateDTO) -> UnitCreateDTO:
    """Create a sample unit DTO."""
    return UnitCreateDTO(
        unit_name="ДНД «Всеволожский дозор»",
        shifts=[sample_shift_dto],
    )


@pytest.fixture
def sample_schedule_dto(sample_unit_dto: UnitCreateDTO) -> ScheduleCreateDTO:
    """Create a sample schedule DTO."""
    return ScheduleCreateDTO(
        month=Month.OCTOBER,
        year=2025,
        units=[sample_unit_dto],
    )


@pytest.fixture
def sample_schedule() -> Schedule:
    """Create a sample schedule model."""
    metadata = ScheduleMetadata(
        month=Month.OCTOBER,
        year=2025,
        created_at=datetime(2025, 10, 1, 12, 0, 0),
    )
    unit = Unit(
        id=1,
        unit_name="ДНД «Всеволожский дозор»",
        shifts=[
            Shift(date="07.10.2025", duty_type=DutyType.UUP),
            Shift(date="15.10.2025", duty_type=DutyType.PDN),
        ],
    )
    schedule = Schedule(metadata=metadata, units=[unit])
    return schedule


# ═══════════════════════════════════════════════════════════
# Create Operations Tests
# ═══════════════════════════════════════════════════════════


class TestCreateSchedule:
    """Test cases for schedule creation."""

    def test_create_schedule_success(
        self,
        schedule_service: ScheduleService,
        sample_schedule_dto: ScheduleCreateDTO,
        mock_repository: Mock,
    ) -> None:
        """Test successful schedule creation."""
        # Act
        result = schedule_service.create_schedule(sample_schedule_dto)

        # Assert
        assert isinstance(result, ScheduleResponseDTO)
        assert result.metadata.year == 2025
        assert result.metadata.month == "октябрь"
        assert len(result.schedule) == 1
        assert len(result.schedule[0].shifts) == 1

        # Verify repository was called
        mock_repository.save.assert_called_once()

    def test_create_schedule_with_multiple_units(
        self,
        schedule_service: ScheduleService,
        sample_shift_dto: ShiftCreateDTO,
        mock_repository: Mock,
    ) -> None:
        """Test creating schedule with multiple units."""
        # Arrange
        unit1 = UnitCreateDTO(
            unit_name="ДНД «Всеволожский дозор»",
            shifts=[sample_shift_dto],
        )
        unit2 = UnitCreateDTO(
            unit_name="ДНД «Заневское ГП»",
            shifts=[
                ShiftCreateDTO(
                    date="08.10.2025",
                    duty_type=DutyType.PDN,
                )
            ],
        )
        dto = ScheduleCreateDTO(month=Month.OCTOBER, year=2025, units=[unit1, unit2])

        # Act
        result = schedule_service.create_schedule(dto)

        # Assert
        assert len(result.schedule) == 2
        assert result.schedule[0].unit_name == "ДНД «Всеволожский дозор»"
        assert result.schedule[1].unit_name == "ДНД «Заневское ГП»"
        mock_repository.save.assert_called_once()

    def test_create_schedule_with_empty_units(
        self,
        schedule_service: ScheduleService,
        mock_repository: Mock,
    ) -> None:
        """Test creating schedule with unit that has no shifts."""
        # Arrange
        unit = UnitCreateDTO(
            unit_name="ДНД «Всеволожский дозор»",
            shifts=[],  # Empty shifts
        )
        dto = ScheduleCreateDTO(month=Month.OCTOBER, year=2025, units=[unit])

        # Act
        result = schedule_service.create_schedule(dto)

        # Assert
        assert len(result.schedule) == 1
        assert len(result.schedule[0].shifts) == 0
        mock_repository.save.assert_called_once()

    def test_create_schedule_metadata_generation(
        self,
        schedule_service: ScheduleService,
        sample_schedule_dto: ScheduleCreateDTO,
    ) -> None:
        """Test that metadata is correctly generated."""
        # Act
        result = schedule_service.create_schedule(sample_schedule_dto)

        # Assert
        assert result.metadata.document_type == "patrol_schedule"
        assert result.metadata.created_by == "manual_input"
        assert isinstance(result.metadata.created_at, datetime)


class TestAddShiftToUnit:
    """Test cases for adding shifts to units."""

    def test_add_shift_to_unit_success(
        self,
        schedule_service: ScheduleService,
        sample_schedule: Schedule,
        sample_shift_dto: ShiftCreateDTO,
        mock_repository: Mock,
    ) -> None:
        """Test successfully adding a shift to a unit."""
        # Arrange
        mock_repository.load.return_value = sample_schedule
        new_shift = ShiftCreateDTO(
            date="20.10.2025",
            duty_type=DutyType.PPSP,
        )

        # Act
        result = schedule_service.add_shift_to_unit(
            schedule_id="test_schedule.json",
            unit_name="ДНД «Всеволожский дозор»",
            shift_dto=new_shift,
        )

        # Assert
        assert isinstance(result, ScheduleResponseDTO)
        mock_repository.load.assert_called_once()
        mock_repository.save.assert_called_once()

    def test_add_shift_to_nonexistent_unit(
        self,
        schedule_service: ScheduleService,
        sample_schedule: Schedule,
        sample_shift_dto: ShiftCreateDTO,
        mock_repository: Mock,
    ) -> None:
        """Test adding shift to non-existent unit raises error."""
        # Arrange
        mock_repository.load.return_value = sample_schedule

        # Act & Assert
        with pytest.raises(UnitNotFoundError):
            schedule_service.add_shift_to_unit(
                schedule_id="test_schedule.json",
                unit_name="Non-existent Unit",
                shift_dto=sample_shift_dto,
            )

    def test_add_shift_to_unit_schedule_not_found(
        self,
        schedule_service: ScheduleService,
        sample_shift_dto: ShiftCreateDTO,
        mock_repository: Mock,
    ) -> None:
        """Test adding shift when schedule doesn't exist."""
        # Arrange
        mock_repository.exists.return_value = False

        # Act & Assert
        with pytest.raises(ScheduleNotFoundError):
            schedule_service.add_shift_to_unit(
                schedule_id="nonexistent.json",
                unit_name="ДНД «Всеволожский дозор»",
                shift_dto=sample_shift_dto,
            )


# ═══════════════════════════════════════════════════════════
# Read Operations Tests
# ═══════════════════════════════════════════════════════════


class TestGetSchedule:
    """Test cases for retrieving schedules."""

    def test_get_schedule_success(
        self,
        schedule_service: ScheduleService,
        sample_schedule: Schedule,
        mock_repository: Mock,
    ) -> None:
        """Test successfully retrieving a schedule."""
        # Arrange
        mock_repository.load.return_value = sample_schedule

        # Act
        result = schedule_service.get_schedule("test_schedule.json")

        # Assert
        assert isinstance(result, ScheduleResponseDTO)
        assert result.metadata.year == 2025
        assert len(result.schedule) == 1
        mock_repository.load.assert_called_once()

    def test_get_schedule_not_found(
        self,
        schedule_service: ScheduleService,
        mock_repository: Mock,
    ) -> None:
        """Test retrieving non-existent schedule raises error."""
        # Arrange
        mock_repository.exists.return_value = False

        # Act & Assert
        with pytest.raises(ScheduleNotFoundError):
            schedule_service.get_schedule("nonexistent.json")

    def test_get_schedule_with_different_id_formats(
        self,
        schedule_service: ScheduleService,
        sample_schedule: Schedule,
        mock_repository: Mock,
    ) -> None:
        """Test that different ID formats work correctly."""
        # Arrange
        mock_repository.load.return_value = sample_schedule

        # Test with filename
        result1 = schedule_service.get_schedule("schedule_2025_10.json")
        assert isinstance(result1, ScheduleResponseDTO)

        # Test with year_month format
        result2 = schedule_service.get_schedule("2025_10")
        assert isinstance(result2, ScheduleResponseDTO)


class TestListSchedules:
    """Test cases for listing schedules."""

    def test_list_schedules_empty(
        self,
        schedule_service: ScheduleService,
        mock_repository: Mock,
    ) -> None:
        """Test listing schedules when none exist."""
        # Arrange
        mock_repository.list_schedules.return_value = []

        # Act
        result = schedule_service.list_schedules()

        # Assert
        assert isinstance(result, list)
        assert len(result) == 0

    def test_list_schedules_with_data(
        self,
        schedule_service: ScheduleService,
        mock_repository: Mock,
        tmp_path: Path,
    ) -> None:
        """Test listing schedules with data."""
        # Arrange
        schedule_file = tmp_path / "schedule_2025_10.json"
        mock_repository.list_schedules.return_value = [schedule_file]
        mock_repository.get_schedule_metadata.return_value = {
            "month": "октябрь",
            "year": 2025,
            "created_at": "2025-10-01T12:00:00",
            "unit_count": 2,
            "total_shifts": 5,
        }

        # Act
        result = schedule_service.list_schedules()

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], ScheduleListItemDTO)
        assert result[0].month == "октябрь"
        assert result[0].year == 2025
        assert result[0].total_shifts == 5

    def test_list_schedules_skips_invalid_files(
        self,
        schedule_service: ScheduleService,
        mock_repository: Mock,
        tmp_path: Path,
    ) -> None:
        """Test that invalid files are skipped when listing."""
        # Arrange
        file1 = tmp_path / "valid.json"
        file2 = tmp_path / "invalid.json"
        mock_repository.list_schedules.return_value = [file1, file2]

        # First file returns valid metadata, second raises exception
        mock_repository.get_schedule_metadata.side_effect = [
            {
                "month": "октябрь",
                "year": 2025,
                "created_at": "2025-10-01T12:00:00",
                "unit_count": 1,
                "total_shifts": 3,
            },
            Exception("Invalid file"),
        ]

        # Act
        result = schedule_service.list_schedules()

        # Assert
        assert len(result) == 1  # Only valid file
        assert result[0].month == "октябрь"


class TestGetUnitShifts:
    """Test cases for getting unit shifts."""

    def test_get_unit_shifts_success(
        self,
        schedule_service: ScheduleService,
        sample_schedule: Schedule,
        mock_repository: Mock,
    ) -> None:
        """Test successfully getting unit shifts."""
        # Arrange
        mock_repository.load.return_value = sample_schedule

        # Act
        result = schedule_service.get_unit_shifts(
            schedule_id="test.json",
            unit_name="ДНД «Всеволожский дозор»",
        )

        # Assert
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(shift, Shift) for shift in result)

    def test_get_unit_shifts_unit_not_found(
        self,
        schedule_service: ScheduleService,
        sample_schedule: Schedule,
        mock_repository: Mock,
    ) -> None:
        """Test getting shifts for non-existent unit."""
        # Arrange
        mock_repository.load.return_value = sample_schedule

        # Act & Assert
        with pytest.raises(UnitNotFoundError):
            schedule_service.get_unit_shifts(
                schedule_id="test.json",
                unit_name="Non-existent Unit",
            )


# ═══════════════════════════════════════════════════════════
# Update Operations Tests
# ═══════════════════════════════════════════════════════════


class TestUpdateShift:
    """Test cases for updating shifts."""

    def test_update_shift_success(
        self,
        schedule_service: ScheduleService,
        sample_schedule: Schedule,
        mock_repository: Mock,
    ) -> None:
        """Test successfully updating a shift."""
        # Arrange
        mock_repository.load.return_value = sample_schedule
        new_shift_dto = ShiftCreateDTO(
            date="07.10.2025",
            duty_type=DutyType.PPSP,  # Changed type
            time="19:00-23:00",  # Changed time
        )

        # Act
        result = schedule_service.update_shift(
            schedule_id="test.json",
            unit_name="ДНД «Всеволожский дозор»",
            old_date="07.10.2025",
            new_shift_dto=new_shift_dto,
        )

        # Assert
        assert isinstance(result, ScheduleResponseDTO)
        mock_repository.save.assert_called_once()

    def test_update_nonexistent_shift(
        self,
        schedule_service: ScheduleService,
        sample_schedule: Schedule,
        mock_repository: Mock,
    ) -> None:
        """Test updating non-existent shift raises error."""
        # Arrange
        mock_repository.load.return_value = sample_schedule
        new_shift_dto = ShiftCreateDTO(
            date="99.10.2025",  # Non-existent date
            duty_type=DutyType.UUP,
        )

        # Act & Assert
        with pytest.raises(DomainValidationError):
            schedule_service.update_shift(
                schedule_id="test.json",
                unit_name="ДНД «Всеволожский дозор»",
                old_date="99.10.2025",
                new_shift_dto=new_shift_dto,
            )


# ═══════════════════════════════════════════════════════════
# Delete Operations Tests
# ═══════════════════════════════════════════════════════════


class TestDeleteShift:
    """Test cases for deleting shifts."""

    def test_delete_shift_success(
        self,
        schedule_service: ScheduleService,
        sample_schedule: Schedule,
        mock_repository: Mock,
    ) -> None:
        """Test successfully deleting a shift."""
        # Arrange
        mock_repository.load.return_value = sample_schedule

        # Act
        result = schedule_service.delete_shift(
            schedule_id="test.json",
            unit_name="ДНД «Всеволожский дозор»",
            date="07.10.2025",
        )

        # Assert
        assert isinstance(result, ScheduleResponseDTO)
        mock_repository.save.assert_called_once()

    def test_delete_shift_from_nonexistent_unit(
        self,
        schedule_service: ScheduleService,
        sample_schedule: Schedule,
        mock_repository: Mock,
    ) -> None:
        """Test deleting shift from non-existent unit."""
        # Arrange
        mock_repository.load.return_value = sample_schedule

        # Act & Assert
        with pytest.raises(UnitNotFoundError):
            schedule_service.delete_shift(
                schedule_id="test.json",
                unit_name="Non-existent Unit",
                date="07.10.2025",
            )


class TestDeleteSchedule:
    """Test cases for deleting schedules."""

    def test_delete_schedule_success(
        self,
        schedule_service: ScheduleService,
        mock_repository: Mock,
    ) -> None:
        """Test successfully deleting a schedule."""
        # Arrange
        mock_repository.delete.return_value = True

        # Act
        result = schedule_service.delete_schedule("test.json")

        # Assert
        assert result is True
        mock_repository.delete.assert_called_once()

    def test_delete_schedule_failure(
        self,
        schedule_service: ScheduleService,
        mock_repository: Mock,
    ) -> None:
        """Test delete schedule returns False on failure."""
        # Arrange
        mock_repository.delete.return_value = False

        # Act
        result = schedule_service.delete_schedule("test.json")

        # Assert
        assert result is False


# ═══════════════════════════════════════════════════════════
# Validation Operations Tests
# ═══════════════════════════════════════════════════════════


class TestValidateSchedule:
    """Test cases for schedule validation."""

    def test_validate_schedule_success(
        self,
        schedule_service: ScheduleService,
        sample_schedule_dto: ScheduleCreateDTO,
        mock_repository: Mock,
    ) -> None:
        """Test validating a valid schedule."""
        # Arrange
        mock_repository.exists.return_value = False

        # Act
        result = schedule_service.validate_schedule(sample_schedule_dto)

        # Assert
        assert isinstance(result, ValidationResultDTO)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_schedule_duplicate_shifts(
        self,
        schedule_service: ScheduleService,
    ) -> None:
        """Test validation catches duplicate shifts."""
        # Arrange
        shift1 = ShiftCreateDTO(date="07.10.2025", duty_type=DutyType.UUP)
        shift2 = ShiftCreateDTO(date="07.10.2025", duty_type=DutyType.PDN)
        unit = UnitCreateDTO(
            unit_name="ДНД «Всеволожский дозор»",
            shifts=[shift1, shift2],  # Duplicate dates
        )
        dto = ScheduleCreateDTO(month=Month.OCTOBER, year=2025, units=[unit])

        # Act
        result = schedule_service.validate_schedule(dto)

        # Assert
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert "Duplicate shift" in result.errors[0]

    def test_validate_schedule_empty_shifts_warning(
        self,
        schedule_service: ScheduleService,
        mock_repository: Mock,
    ) -> None:
        """Test validation warns about empty shifts."""
        # Arrange
        unit = UnitCreateDTO(
            unit_name="ДНД «Всеволожский дозор»",
            shifts=[],  # No shifts
        )
        dto = ScheduleCreateDTO(month=Month.OCTOBER, year=2025, units=[unit])
        mock_repository.exists.return_value = False

        # Act
        result = schedule_service.validate_schedule(dto)

        # Assert
        assert result.is_valid is True  # Valid but has warning
        assert len(result.warnings) > 0
        assert "No shifts" in result.warnings[0]

    def test_validate_schedule_already_exists_warning(
        self,
        schedule_service: ScheduleService,
        sample_schedule_dto: ScheduleCreateDTO,
        mock_repository: Mock,
    ) -> None:
        """Test validation warns if schedule already exists."""
        # Arrange
        mock_repository.exists.return_value = True

        # Act
        result = schedule_service.validate_schedule(sample_schedule_dto)

        # Assert
        assert result.is_valid is True
        assert len(result.warnings) > 0
        assert "already exists" in result.warnings[0]


# ═══════════════════════════════════════════════════════════
# Statistics Operations Tests
# ═══════════════════════════════════════════════════════════


class TestGetScheduleStatistics:
    """Test cases for schedule statistics."""

    def test_get_statistics_success(
        self,
        schedule_service: ScheduleService,
        sample_schedule: Schedule,
        mock_repository: Mock,
    ) -> None:
        """Test successfully getting schedule statistics."""
        # Arrange
        mock_repository.load.return_value = sample_schedule

        # Act
        result = schedule_service.get_schedule_statistics("test.json")

        # Assert
        assert isinstance(result, ScheduleStatisticsDTO)
        assert result.month == "октябрь"
        assert result.year == 2025
        assert result.total_units == 1
        assert result.total_shifts == 2
        assert len(result.units) == 1

    def test_get_statistics_schedule_not_found(
        self,
        schedule_service: ScheduleService,
        mock_repository: Mock,
    ) -> None:
        """Test getting statistics for non-existent schedule."""
        # Arrange
        mock_repository.exists.return_value = False

        # Act & Assert
        with pytest.raises(ScheduleNotFoundError):
            schedule_service.get_schedule_statistics("nonexistent.json")

    def test_get_statistics_unit_details(
        self,
        schedule_service: ScheduleService,
        mock_repository: Mock,
    ) -> None:
        """Test that unit statistics are correctly calculated."""
        # Arrange
        metadata = ScheduleMetadata(month=Month.OCTOBER, year=2025)
        unit = Unit(
            id=1,
            unit_name="ДНД «Всеволожский дозор»",
            shifts=[
                Shift(date="07.10.2025", duty_type=DutyType.UUP),
                Shift(date="15.10.2025", duty_type=DutyType.UUP),
                Shift(date="22.10.2025", duty_type=DutyType.PDN),
            ],
        )
        schedule = Schedule(metadata=metadata, units=[unit])
        mock_repository.load.return_value = schedule

        # Act
        result = schedule_service.get_schedule_statistics("test.json")

        # Assert
        unit_stats = result.units[0]
        assert unit_stats.total_shifts == 3
        assert unit_stats.shifts_by_type["УУП"] == 2
        assert unit_stats.shifts_by_type["ПДН"] == 1


# ═══════════════════════════════════════════════════════════
# Helper Methods Tests
# ═══════════════════════════════════════════════════════════


class TestHelperMethods:
    """Test cases for helper methods."""

    def test_resolve_schedule_path_with_full_path(
        self, schedule_service: ScheduleService
    ) -> None:
        """Test resolving full path."""
        # Act
        result = schedule_service._resolve_schedule_path("/full/path/to/schedule.json")

        # Assert
        assert str(result) == "/full/path/to/schedule.json"

    def test_resolve_schedule_path_with_filename(
        self, schedule_service: ScheduleService
    ) -> None:
        """Test resolving just filename."""
        # Act
        result = schedule_service._resolve_schedule_path("schedule_2025_10.json")

        # Assert
        assert result.name == "schedule_2025_10.json"
        assert "data" in str(result)

    def test_resolve_schedule_path_with_year_month(
        self, schedule_service: ScheduleService
    ) -> None:
        """Test resolving year_month format."""
        # Act
        result = schedule_service._resolve_schedule_path("2025_10")

        # Assert
        assert result.name == "schedule_2025_10.json"

    def test_schedule_to_response_dto_conversion(
        self, schedule_service: ScheduleService, sample_schedule: Schedule
    ) -> None:
        """Test converting schedule to response DTO."""
        # Act
        result = schedule_service._schedule_to_response_dto(sample_schedule)

        # Assert
        assert isinstance(result, ScheduleResponseDTO)
        assert result.metadata.year == 2025
        assert result.metadata.month == "октябрь"
        assert len(result.schedule) == 1
        assert len(result.schedule[0].shifts) == 2
