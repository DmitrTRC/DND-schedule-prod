"""
Base command class for CLI.

Author: DmitrTRC
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from rich.console import Console

from schedule_dnd.application.services.export_service import ExportService
from schedule_dnd.application.services.schedule_service import ScheduleService
from schedule_dnd.infrastructure.config.settings import get_settings
from schedule_dnd.infrastructure.repositories.json_repository import JSONRepository


class BaseCommand(ABC):
    """Abstract base class for CLI commands."""

    def __init__(self) -> None:
        """Initialize command."""
        self.console = Console()
        self.settings = get_settings()

        # Initialize services
        self.repository = JSONRepository()
        self.schedule_service = ScheduleService(self.repository)
        self.export_service = ExportService(self.repository)

    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> int:
        """
        Execute the command.

        Returns:
            Exit code (0 for success, non-zero for error)
        """
        pass

    def success(self, message: str) -> None:
        """Print success message."""
        self.console.print(f"✓ {message}", style="bold green")

    def error(self, message: str) -> None:
        """Print error message."""
        self.console.print(f"✗ {message}", style="bold red")

    def warning(self, message: str) -> None:
        """Print warning message."""
        self.console.print(f"⚠ {message}", style="bold yellow")

    def info(self, message: str) -> None:
        """Print info message."""
        self.console.print(f"ℹ {message}", style="bold blue")

    def prompt(self, message: str, default: Optional[str] = None) -> str:
        """
        Prompt user for input.

        Args:
            message: Prompt message
            default: Default value if user just presses Enter

        Returns:
            User input
        """
        if default:
            prompt_text = f"{message} [{default}]: "
        else:
            prompt_text = f"{message}: "

        try:
            response = input(prompt_text).strip()
            return response if response else (default or "")
        except EOFError:
            return default or ""

    def confirm(self, message: str, default: bool = True) -> bool:
        """
        Ask user for yes/no confirmation.

        Args:
            message: Confirmation message
            default: Default value

        Returns:
            True if user confirms
        """
        default_str = "Y/n" if default else "y/N"
        response = self.prompt(f"{message} [{default_str}]", "").lower()

        if not response:
            return default

        return response in ("y", "yes", "да", "д")
