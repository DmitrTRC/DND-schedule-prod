"""
JSON repository implementation.

Handles saving and loading schedules in JSON format.
Author: DmitrTRC
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

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
from schedule_dnd.infrastructure.config.settings import get_settings
from schedule_dnd.infrastructure.repositories.base import ScheduleRepository


class JSONRepository(ScheduleRepository):
    """Repository for JSON-based schedule storage."""

    def __init__(self, base_dir: Optional[Path] = None) -> None:
        """
        Initialize JSON repository.

        Args:
            base_dir: Base directory for schedules (uses settings if None)
        """
        self.settings = get_settings()
        self.base_dir = base_dir or self.settings.data_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, schedule: Schedule, filepath: Optional[Path] = None) -> Path:
        """
        Save a schedule to a JSON file.

        Args:
            schedule: Schedule to save
            filepath: Optional custom file path

        Returns:
            Path to the saved file

        Raises:
            FileSystemError: If save operation fails
        """
        if filepath is None:
            filepath = self._get_default_path(schedule)

        # Create backup if file exists and backup is enabled
        if filepath.exists() and self.settings.enable_backup:
            try:
                self.backup(filepath)
            except Exception as e:
                # Log warning but continue with save
                print(f"Warning: Backup creation failed: {e}")

        try:
            # Convert schedule to dictionary
            data = self._schedule_to_dict(schedule)

            # Write to file
            with open(filepath, "w", encoding="utf-8") as f:
                if self.settings.pretty_json:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                else:
                    json.dump(data, f, ensure_ascii=False)

            return filepath

        except (OSError, IOError) as e:
            raise FileSystemError(
                message=f"Failed to save schedule to {filepath}",
                details={"path": str(filepath), "error": str(e)},
            ) from e
        except Exception as e:
            raise SerializationError(
                format_type="JSON", reason=f"Failed to serialize schedule: {str(e)}"
            ) from e

    def load(self, filepath: Path) -> Schedule:
        """
        Load a schedule from a JSON file.

        Args:
            filepath: Path to the schedule file

        Returns:
            Loaded schedule

        Raises:
            FileNotFoundError: If file doesn't exist
            SerializationError: If deserialization fails
        """
        if not filepath.exists():
            raise ScheduleFileNotFoundError(str(filepath))

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            return self._dict_to_schedule(data)

        except json.JSONDecodeError as e:
            raise SerializationError(
                format_type="JSON",
                reason=f"Invalid JSON in file {filepath}: {str(e)}",
            ) from e
        except (OSError, IOError) as e:
            raise FileSystemError(
                message=f"Failed to read schedule from {filepath}",
                details={"path": str(filepath), "error": str(e)},
            ) from e
        except Exception as e:
            raise SerializationError(
                format_type="JSON",
                reason=f"Failed to deserialize schedule: {str(e)}",
            ) from e

    def exists(self, filepath: Path) -> bool:
        """
        Check if a schedule file exists.

        Args:
            filepath: Path to check

        Returns:
            True if file exists
        """
        return filepath.exists() and filepath.is_file()

    def delete(self, filepath: Path) -> bool:
        """
        Delete a schedule file.

        Args:
            filepath: Path to the file

        Returns:
            True if deletion was successful

        Raises:
            FileNotFoundError: If file doesn't exist
            FilePermissionError: If deletion is not allowed
        """
        if not filepath.exists():
            raise ScheduleFileNotFoundError(str(filepath))

        try:
            filepath.unlink()
            return True
        except PermissionError as e:
            raise FilePermissionError(str(filepath), "delete") from e
        except Exception as e:
            raise FileSystemError(
                message=f"Failed to delete {filepath}",
                details={"path": str(filepath), "error": str(e)},
            ) from e

    def list_schedules(self, directory: Optional[Path] = None) -> list[Path]:
        """
        List all schedule files in a directory.

        Args:
            directory: Directory to search (uses default if None)

        Returns:
            List of schedule file paths sorted by modification time (newest first)
        """
        search_dir = directory or self.base_dir

        if not search_dir.exists():
            return []

        # Find all JSON files matching schedule pattern
        schedules = list(search_dir.glob("schedule_*.json"))

        # Sort by modification time (newest first)
        schedules.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        return schedules

    def backup(self, filepath: Path) -> Path:
        """
        Create a backup of a schedule file.

        Args:
            filepath: Path to the file to backup

        Returns:
            Path to the backup file

        Raises:
            FileNotFoundError: If original file doesn't exist
            FileSystemError: If backup creation fails
        """
        if not filepath.exists():
            raise ScheduleFileNotFoundError(str(filepath))

        try:
            # Generate backup path with timestamp
            backup_path = self.settings.get_backup_file_path(filepath)

            # Copy file
            shutil.copy2(filepath, backup_path)

            # Clean old backups if limit is set
            self._cleanup_old_backups(filepath)

            return backup_path

        except Exception as e:
            raise FileSystemError(
                message=f"Failed to create backup of {filepath}",
                details={"path": str(filepath), "error": str(e)},
            ) from e

    def get_schedule_metadata(self, filepath: Path) -> dict[str, str | int | None]:
        """
        Get metadata from a schedule file without loading the entire file.

        Args:
            filepath: Path to the schedule file

        Returns:
            Dictionary with metadata

        Raises:
            FileNotFoundError: If file doesn't exist
            SerializationError: If file is corrupted
        """
        if not filepath.exists():
            raise ScheduleFileNotFoundError(str(filepath))

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            metadata = data.get("metadata", {})

            return {
                "month": metadata.get("month"),
                "year": metadata.get("year"),
                "created_at": metadata.get("created_at"),
                "created_by": metadata.get("created_by"),
                "unit_count": len(data.get("schedule", [])),
                "total_shifts": sum(
                    len(unit.get("shifts", [])) for unit in data.get("schedule", [])
                ),
            }

        except json.JSONDecodeError as e:
            raise SerializationError(
                format_type="JSON",
                reason=f"Invalid JSON in file {filepath}: {str(e)}",
            ) from e
        except Exception as e:
            raise SerializationError(
                format_type="JSON",
                reason=f"Failed to read metadata: {str(e)}",
            ) from e

    # ═══════════════════════════════════════════════════════════
    # Private Methods
    # ═══════════════════════════════════════════════════════════

    def _get_default_path(self, schedule: Schedule) -> Path:
        """Get default file path for a schedule."""
        filename = f"schedule_{schedule.metadata.year}_{schedule.metadata.month.to_number():02d}.json"
        return self.base_dir / filename

    def _schedule_to_dict(self, schedule: Schedule) -> dict[str, Any]:
        """Convert Schedule to dictionary."""
        return {
            "metadata": {
                "document_type": schedule.metadata.document_type,
                "month": schedule.metadata.month.display_name(),
                "year": schedule.metadata.year,
                "created_at": schedule.metadata.created_at.isoformat(),
                "created_by": schedule.metadata.created_by,
                "source": schedule.metadata.source,
                "signatory": schedule.metadata.signatory,
                "note": schedule.metadata.note,
            },
            "schedule": [
                {
                    "id": unit.id,
                    "unit_name": unit.unit_name,
                    "shifts": [
                        {
                            "date": shift.date,
                            "duty_type": shift.duty_type.value,
                            "time": shift.time,
                            "notes": shift.notes,
                        }
                        for shift in unit.shifts
                    ],
                }
                for unit in schedule.units
            ],
        }

    def _dict_to_schedule(self, data: dict[str, Any]) -> Schedule:
        """Convert dictionary to Schedule."""
        # Parse metadata
        metadata_dict = data.get("metadata", {})
        metadata = ScheduleMetadata(
            document_type=metadata_dict.get("document_type", "patrol_schedule"),
            month=Month.from_russian_name(metadata_dict["month"]),
            year=metadata_dict["year"],
            created_at=datetime.fromisoformat(metadata_dict["created_at"]),
            created_by=metadata_dict.get("created_by", "unknown"),
            source=metadata_dict.get("source"),
            signatory=metadata_dict.get("signatory"),
            note=metadata_dict.get("note"),
        )

        # Parse units
        units: list[Unit] = []
        for unit_dict in data.get("schedule", []):
            # Parse shifts
            shifts: list[Shift] = []
            for shift_dict in unit_dict.get("shifts", []):
                shift = Shift(
                    date=shift_dict["date"],
                    duty_type=DutyType(shift_dict["duty_type"]),
                    time=shift_dict.get("time", "18:00-22:00"),
                    notes=shift_dict.get("notes", ""),
                )
                shifts.append(shift)

            # Create unit
            unit = Unit(
                id=unit_dict["id"],
                unit_name=unit_dict["unit_name"],
                shifts=shifts,
            )
            units.append(unit)

        # Create and return schedule
        return Schedule(metadata=metadata, units=units)

    def _cleanup_old_backups(self, original_filepath: Path) -> None:
        """
        Clean up old backup files, keeping only the most recent ones.

        Args:
            original_filepath: Path to the original file
        """
        if not self.settings.enable_backup or self.settings.max_backups <= 0:
            return

        backup_dir = self.settings.data_dir / "backups"
        if not backup_dir.exists():
            return

        # Find all backups for this file
        stem = original_filepath.stem
        pattern = f"{stem}_backup_*.json"
        backups = list(backup_dir.glob(pattern))

        # Sort by modification time (oldest first)
        backups.sort(key=lambda p: p.stat().st_mtime)

        # Remove old backups
        while len(backups) > self.settings.max_backups:
            oldest = backups.pop(0)
            try:
                oldest.unlink()
            except Exception as e:
                print(f"Warning: Failed to delete old backup {oldest}: {e}")
