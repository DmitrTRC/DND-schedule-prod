"""
Unit tests for JSONRepository.

Comprehensive testing of JSON-based schedule persistence.
Author: DmitrTRC
"""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from schedule_dnd.domain.enums import DutyType, Month
from schedule_dnd.domain.exceptions import (
    FileNotFoundError as ScheduleFileNotFoundError,
)
from schedule_dnd.domain.exceptions import (
    FilePermissionError,
    FileSystemError,
    SerializationError,
)
from schedule_dnd.domain.models import Schedule, ScheduleMetadata, Shift, Unit
from schedule_dnd.infrastructure.repositories.json_repository import JSONRepository

# ═══════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def temp_data_dir(tmp_path: Path) -> Path:
    """Create temporary data directory."""
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


@pytest.fixture
def repository(temp_data_dir: Path) -> JSONRepository:
    """Create repository with temporary directory."""
    return JSONRepository(base_dir=temp_data_dir)


@pytest.fixture
def sample_schedule() -> Schedule:
    """Create a sample schedule for testing."""
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
    return Schedule(metadata=metadata, units=[unit])


@pytest.fixture
def sample_json_data() -> dict:
    """Create sample JSON data for testing."""
    return {
        "metadata": {
            "document_type": "patrol_schedule",
            "month": "Октябрь",
            "year": 2025,
            "created_at": "2025-10-01T12:00:00",
            "created_by": "manual_input",
            "source": None,
            "signatory": None,
            "note": None,
        },
        "schedule": [
            {
                "id": 1,
                "unit_name": "ДНД «Всеволожский дозор»",
                "shifts": [
                    {
                        "date": "07.10.2025",
                        "duty_type": "УУП",
                        "time": "18:00-22:00",
                        "notes": "Получение инструкций в ОП. Время: 17:30",
                    }
                ],
            }
        ],
    }


# ═══════════════════════════════════════════════════════════
# Save Operation Tests
# ═══════════════════════════════════════════════════════════


class TestSave:
    """Test cases for saving schedules."""

    def test_save_schedule_success(
        self,
        repository: JSONRepository,
        sample_schedule: Schedule,
        temp_data_dir: Path,
    ) -> None:
        """Test successfully saving a schedule."""
        # Act
        result_path = repository.save(sample_schedule)

        # Assert
        assert result_path.exists()
        assert result_path.parent == temp_data_dir
        assert "schedule_2025_10.json" in str(result_path)

        # Verify file content
        with open(result_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["metadata"]["year"] == 2025
        assert data["metadata"]["month"] == "Октябрь"
        assert len(data["schedule"]) == 1

    def test_save_schedule_custom_path(
        self,
        repository: JSONRepository,
        sample_schedule: Schedule,
        tmp_path: Path,
    ) -> None:
        """Test saving with custom path."""
        # Arrange
        custom_path = tmp_path / "custom" / "my_schedule.json"
        custom_path.parent.mkdir(parents=True, exist_ok=True)

        # Act
        result_path = repository.save(sample_schedule, filepath=custom_path)

        # Assert
        assert result_path == custom_path
        assert result_path.exists()

    def test_save_schedule_overwrites_existing(
        self,
        repository: JSONRepository,
        sample_schedule: Schedule,
        temp_data_dir: Path,
    ) -> None:
        """Test that saving overwrites existing file."""
        # Arrange - save initial schedule
        first_path = repository.save(sample_schedule)

        # Modify schedule
        sample_schedule.units[0].add_shift(
            Shift(date="20.10.2025", duty_type=DutyType.PPSP)
        )

        # Act - save again
        second_path = repository.save(sample_schedule)

        # Assert
        assert first_path == second_path
        assert second_path.exists()

        # Verify updated content
        with open(second_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data["schedule"][0]["shifts"]) == 3

    @patch("schedule_dnd.infrastructure.repositories.json_repository.get_settings")
    def test_save_creates_backup_when_enabled(
        self,
        mock_settings: Mock,
        repository: JSONRepository,
        sample_schedule: Schedule,
        temp_data_dir: Path,
    ) -> None:
        """Test that backup is created when enabled."""
        # Arrange
        mock_settings.return_value.enable_backup = True
        mock_settings.return_value.pretty_json = True
        mock_settings.return_value.data_dir = temp_data_dir

        # Create initial file
        first_path = repository.save(sample_schedule)

        # Modify and save again
        sample_schedule.units[0].add_shift(
            Shift(date="20.10.2025", duty_type=DutyType.PPSP)
        )

        # Act
        with patch.object(repository, "backup") as mock_backup:
            repository.save(sample_schedule, filepath=first_path)

            # Assert backup was called
            mock_backup.assert_called_once_with(first_path)

    def test_save_with_multiple_units(
        self,
        repository: JSONRepository,
        temp_data_dir: Path,
    ) -> None:
        """Test saving schedule with multiple units."""
        # Arrange
        metadata = ScheduleMetadata(month=Month.OCTOBER, year=2025)
        unit1 = Unit(
            id=1,
            unit_name="ДНД «Всеволожский дозор»",
            shifts=[Shift(date="07.10.2025", duty_type=DutyType.UUP)],
        )
        unit2 = Unit(
            id=2,
            unit_name="ДНД «Заневское ГП»",
            shifts=[Shift(date="08.10.2025", duty_type=DutyType.PDN)],
        )
        schedule = Schedule(metadata=metadata, units=[unit1, unit2])

        # Act
        result_path = repository.save(schedule)

        # Assert
        with open(result_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data["schedule"]) == 2
        assert data["schedule"][0]["unit_name"] == "ДНД «Всеволожский дозор»"
        assert data["schedule"][1]["unit_name"] == "ДНД «Заневское ГП»"


# ═══════════════════════════════════════════════════════════
# Load Operation Tests
# ═══════════════════════════════════════════════════════════


class TestLoad:
    """Test cases for loading schedules."""

    def test_load_schedule_success(
        self,
        repository: JSONRepository,
        temp_data_dir: Path,
        sample_json_data: dict,
    ) -> None:
        """Test successfully loading a schedule."""
        # Arrange
        filepath = temp_data_dir / "test_schedule.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(sample_json_data, f)

        # Act
        schedule = repository.load(filepath)

        # Assert
        assert isinstance(schedule, Schedule)
        assert schedule.metadata.year == 2025
        assert schedule.metadata.month == Month.OCTOBER
        assert len(schedule.units) == 1
        assert len(schedule.units[0].shifts) == 1

    def test_load_schedule_file_not_found(
        self,
        repository: JSONRepository,
        temp_data_dir: Path,
    ) -> None:
        """Test loading non-existent file raises error."""
        # Arrange
        nonexistent_path = temp_data_dir / "nonexistent.json"

        # Act & Assert
        with pytest.raises(ScheduleFileNotFoundError):
            repository.load(nonexistent_path)

    def test_load_schedule_invalid_json(
        self,
        repository: JSONRepository,
        temp_data_dir: Path,
    ) -> None:
        """Test loading file with invalid JSON."""
        # Arrange
        filepath = temp_data_dir / "invalid.json"
        with open(filepath, "w") as f:
            f.write("{ invalid json }")

        # Act & Assert
        with pytest.raises(SerializationError):
            repository.load(filepath)

    def test_load_schedule_missing_required_fields(
        self,
        repository: JSONRepository,
        temp_data_dir: Path,
    ) -> None:
        """Test loading file with missing required fields."""
        # Arrange
        filepath = temp_data_dir / "incomplete.json"
        incomplete_data = {
            "metadata": {
                "month": "Октябрь"
                # Missing year and other required fields
            }
        }
        with open(filepath, "w") as f:
            json.dump(incomplete_data, f)

        # Act & Assert
        with pytest.raises(SerializationError):
            repository.load(filepath)

    def test_load_save_roundtrip(
        self,
        repository: JSONRepository,
        sample_schedule: Schedule,
    ) -> None:
        """Test that save → load preserves data."""
        # Act
        saved_path = repository.save(sample_schedule)
        loaded_schedule = repository.load(saved_path)

        # Assert
        assert loaded_schedule.metadata.year == sample_schedule.metadata.year
        assert loaded_schedule.metadata.month == sample_schedule.metadata.month
        assert len(loaded_schedule.units) == len(sample_schedule.units)
        assert len(loaded_schedule.units[0].shifts) == len(
            sample_schedule.units[0].shifts
        )


# ═══════════════════════════════════════════════════════════
# Exists Operation Tests
# ═══════════════════════════════════════════════════════════


class TestExists:
    """Test cases for checking file existence."""

    def test_exists_file_present(
        self,
        repository: JSONRepository,
        temp_data_dir: Path,
    ) -> None:
        """Test exists returns True for existing file."""
        # Arrange
        filepath = temp_data_dir / "test.json"
        filepath.write_text("{}")

        # Act & Assert
        assert repository.exists(filepath) is True

    def test_exists_file_absent(
        self,
        repository: JSONRepository,
        temp_data_dir: Path,
    ) -> None:
        """Test exists returns False for non-existent file."""
        # Arrange
        filepath = temp_data_dir / "nonexistent.json"

        # Act & Assert
        assert repository.exists(filepath) is False

    def test_exists_directory(
        self,
        repository: JSONRepository,
        temp_data_dir: Path,
    ) -> None:
        """Test exists returns False for directory."""
        # Arrange
        dirpath = temp_data_dir / "test_dir"
        dirpath.mkdir()

        # Act & Assert
        assert repository.exists(dirpath) is False


# ═══════════════════════════════════════════════════════════
# Delete Operation Tests
# ═══════════════════════════════════════════════════════════


class TestDelete:
    """Test cases for deleting schedules."""

    def test_delete_success(
        self,
        repository: JSONRepository,
        temp_data_dir: Path,
    ) -> None:
        """Test successfully deleting a file."""
        # Arrange
        filepath = temp_data_dir / "test.json"
        filepath.write_text("{}")

        # Act
        result = repository.delete(filepath)

        # Assert
        assert result is True
        assert not filepath.exists()

    def test_delete_file_not_found(
        self,
        repository: JSONRepository,
        temp_data_dir: Path,
    ) -> None:
        """Test deleting non-existent file raises error."""
        # Arrange
        filepath = temp_data_dir / "nonexistent.json"

        # Act & Assert
        with pytest.raises(ScheduleFileNotFoundError):
            repository.delete(filepath)


# ═══════════════════════════════════════════════════════════
# List Schedules Tests
# ═══════════════════════════════════════════════════════════


class TestListSchedules:
    """Test cases for listing schedules."""

    def test_list_schedules_empty_directory(
        self,
        repository: JSONRepository,
    ) -> None:
        """Test listing schedules in empty directory."""
        # Act
        schedules = repository.list_schedules()

        # Assert
        assert isinstance(schedules, list)
        assert len(schedules) == 0

    def test_list_schedules_with_files(
        self,
        repository: JSONRepository,
        temp_data_dir: Path,
    ) -> None:
        """Test listing schedules with multiple files."""
        # Arrange
        (temp_data_dir / "schedule_2025_10.json").write_text("{}")
        (temp_data_dir / "schedule_2025_11.json").write_text("{}")
        (temp_data_dir / "not_a_schedule.json").write_text("{}")

        # Act
        schedules = repository.list_schedules()

        # Assert
        assert len(schedules) == 2
        assert all("schedule_" in str(s) for s in schedules)

    def test_list_schedules_sorted_by_time(
        self,
        repository: JSONRepository,
        temp_data_dir: Path,
    ) -> None:
        """Test that schedules are sorted by modification time."""
        # Arrange
        import time

        file1 = temp_data_dir / "schedule_2025_10.json"
        file2 = temp_data_dir / "schedule_2025_11.json"

        file1.write_text("{}")
        time.sleep(0.01)
        file2.write_text("{}")

        # Act
        schedules = repository.list_schedules()

        # Assert - newest first
        assert len(schedules) == 2
        assert schedules[0] == file2
        assert schedules[1] == file1

    def test_list_schedules_nonexistent_directory(
        self,
        temp_data_dir: Path,
    ) -> None:
        """Test listing schedules in non-existent directory."""
        # Arrange
        nonexistent_dir = temp_data_dir / "nonexistent"
        repository = JSONRepository(base_dir=nonexistent_dir)

        # Act
        schedules = repository.list_schedules()

        # Assert
        assert len(schedules) == 0


# ═══════════════════════════════════════════════════════════
# Backup Tests
# ═══════════════════════════════════════════════════════════


class TestBackup:
    """Test cases for backup operations."""

    def test_backup_success(
        self,
        repository: JSONRepository,
        temp_data_dir: Path,
    ) -> None:
        """Test successfully creating a backup."""
        # Arrange
        filepath = temp_data_dir / "test.json"
        filepath.write_text('{"test": "data"}')

        # Act
        backup_path = repository.backup(filepath)

        # Assert - check backup was created
        assert backup_path.exists(), "Backup file should exist"
        assert backup_path != filepath, "Backup should be different from original"

        # Check backup is in a 'backups' directory
        assert "backups" in str(backup_path), "Backup should be in backups directory"

        # Check backup filename pattern
        assert (
            "test_backup_" in backup_path.name
        ), "Backup should have backup pattern in name"
        assert backup_path.suffix == ".json", "Backup should have same extension"

        # Verify backup content matches original
        with open(backup_path, "r") as f:
            backup_content = f.read()
        assert (
            backup_content == '{"test": "data"}'
        ), "Backup content should match original"

    def test_backup_file_not_found(
        self,
        repository: JSONRepository,
        temp_data_dir: Path,
    ) -> None:
        """Test backup of non-existent file raises error."""
        # Arrange
        filepath = temp_data_dir / "nonexistent.json"

        # Act & Assert
        with pytest.raises(ScheduleFileNotFoundError):
            repository.backup(filepath)


# ═══════════════════════════════════════════════════════════
# Get Metadata Tests
# ═══════════════════════════════════════════════════════════


class TestGetMetadata:
    """Test cases for getting schedule metadata."""

    def test_get_metadata_success(
        self,
        repository: JSONRepository,
        temp_data_dir: Path,
        sample_json_data: dict,
    ) -> None:
        """Test successfully getting metadata."""
        # Arrange
        filepath = temp_data_dir / "test.json"
        with open(filepath, "w") as f:
            json.dump(sample_json_data, f)

        # Act
        metadata = repository.get_schedule_metadata(filepath)

        # Assert
        assert metadata["month"] == "Октябрь"
        assert metadata["year"] == 2025
        assert metadata["unit_count"] == 1
        assert metadata["total_shifts"] == 1

    def test_get_metadata_file_not_found(
        self,
        repository: JSONRepository,
        temp_data_dir: Path,
    ) -> None:
        """Test getting metadata for non-existent file."""
        # Arrange
        filepath = temp_data_dir / "nonexistent.json"

        # Act & Assert
        with pytest.raises(ScheduleFileNotFoundError):
            repository.get_schedule_metadata(filepath)

    def test_get_metadata_invalid_json(
        self,
        repository: JSONRepository,
        temp_data_dir: Path,
    ) -> None:
        """Test getting metadata from invalid JSON."""
        # Arrange
        filepath = temp_data_dir / "invalid.json"
        with open(filepath, "w") as f:
            f.write("{ invalid json }")

        # Act & Assert
        with pytest.raises(SerializationError):
            repository.get_schedule_metadata(filepath)


# ═══════════════════════════════════════════════════════════
# Private Methods Tests
# ═══════════════════════════════════════════════════════════


class TestPrivateMethods:
    """Test cases for private helper methods."""

    def test_get_default_path(
        self,
        repository: JSONRepository,
        sample_schedule: Schedule,
    ) -> None:
        """Test generating default file path."""
        # Act
        path = repository._get_default_path(sample_schedule)

        # Assert
        assert "schedule_2025_10.json" in str(path)
        assert path.parent == repository.base_dir

    def test_schedule_to_dict(
        self,
        repository: JSONRepository,
        sample_schedule: Schedule,
    ) -> None:
        """Test converting schedule to dictionary."""
        # Act
        data = repository._schedule_to_dict(sample_schedule)

        # Assert
        assert "metadata" in data
        assert "schedule" in data
        assert data["metadata"]["year"] == 2025
        assert data["metadata"]["month"] == "Октябрь"
        assert len(data["schedule"]) == 1

    def test_dict_to_schedule(
        self,
        repository: JSONRepository,
        sample_json_data: dict,
    ) -> None:
        """Test converting dictionary to schedule."""
        # Act
        schedule = repository._dict_to_schedule(sample_json_data)

        # Assert
        assert isinstance(schedule, Schedule)
        assert schedule.metadata.year == 2025
        assert schedule.metadata.month == Month.OCTOBER
        assert len(schedule.units) == 1
