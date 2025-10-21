"""
Abstract repository base class.

Defines the contract for data repositories.
Author: DmitrTRC
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from schedule_dnd.domain.models import Schedule


class ScheduleRepository(ABC):
    """Abstract base class for schedule repositories."""

    @abstractmethod
    def save(self, schedule: Schedule, filepath: Optional[Path] = None) -> Path:
        """
        Save a schedule to storage.

        Args:
            schedule: Schedule to save
            filepath: Optional custom file path

        Returns:
            Path to the saved file

        Raises:
            FileSystemError: If save operation fails
        """
        pass

    @abstractmethod
    def load(self, filepath: Path) -> Schedule:
        """
        Load a schedule from storage.

        Args:
            filepath: Path to the schedule file

        Returns:
            Loaded schedule

        Raises:
            FileNotFoundError: If file doesn't exist
            SerializationError: If deserialization fails
        """
        pass

    @abstractmethod
    def exists(self, filepath: Path) -> bool:
        """
        Check if a schedule file exists.

        Args:
            filepath: Path to check

        Returns:
            True if file exists
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def list_schedules(self, directory: Optional[Path] = None) -> list[Path]:
        """
        List all schedule files in a directory.

        Args:
            directory: Directory to search (uses default if None)

        Returns:
            List of schedule file paths
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def get_schedule_metadata(self, filepath: Path) -> dict[str, str | int | None]:
        """
        Get metadata from a schedule file without loading the entire file.

        Args:
            filepath: Path to the schedule file

        Returns:
            Dictionary with metadata (month, year, created_at, etc.)

        Raises:
            FileNotFoundError: If file doesn't exist
            SerializationError: If file is corrupted
        """
        pass
