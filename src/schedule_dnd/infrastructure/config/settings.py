"""
Application settings using Pydantic Settings.

This module manages configuration from environment variables and .env files.
Author: DmitrTRC
"""

from pathlib import Path
from typing import Any, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from schedule_dnd.domain.constants import APP_NAME, APP_VERSION
from schedule_dnd.domain.enums import Environment


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    # ═══════════════════════════════════════════════════════════
    # Application
    # ═══════════════════════════════════════════════════════════

    app_name: str = Field(default=APP_NAME, description="Application name")
    app_version: str = Field(default=APP_VERSION, description="Application version")
    environment: Environment = Field(
        default=Environment.PRODUCTION, description="Runtime environment"
    )
    debug: bool = Field(default=False, description="Enable debug mode")

    # ═══════════════════════════════════════════════════════════
    # Paths
    # ═══════════════════════════════════════════════════════════

    base_dir: Path = Field(
        default_factory=lambda: Path.cwd(), description="Base directory"
    )
    data_dir: Path = Field(
        default_factory=lambda: Path.cwd() / "data",
        description="Data storage directory",
    )
    output_dir: Path = Field(
        default_factory=lambda: Path.cwd() / "output",
        description="Export output directory",
    )
    log_dir: Path = Field(
        default_factory=lambda: Path.cwd() / "logs", description="Log files directory"
    )

    # ═══════════════════════════════════════════════════════════
    # Features
    # ═══════════════════════════════════════════════════════════

    enable_autosave: bool = Field(
        default=True, description="Enable automatic saving of schedules"
    )
    autosave_interval: int = Field(
        default=180, description="Autosave interval in seconds", ge=30, le=600
    )
    enable_backup: bool = Field(
        default=True, description="Enable backup creation before overwrites"
    )
    max_backups: int = Field(
        default=5, description="Maximum number of backups to keep", ge=1, le=20
    )

    # ═══════════════════════════════════════════════════════════
    # Validation
    # ═══════════════════════════════════════════════════════════

    strict_validation: bool = Field(
        default=True, description="Enable strict validation rules"
    )
    allow_past_dates: bool = Field(default=False, description="Allow dates in the past")
    allow_duplicate_shifts: bool = Field(
        default=False, description="Allow duplicate shifts for same unit/date"
    )
    max_shifts_per_unit: int = Field(
        default=50, description="Maximum shifts per unit per month", ge=10, le=100
    )

    # ═══════════════════════════════════════════════════════════
    # Export
    # ═══════════════════════════════════════════════════════════

    default_export_format: str = Field(
        default="json", description="Default export format"
    )
    excel_author: str = Field(
        default="Schedule DND", description="Author name in Excel exports"
    )
    include_metadata: bool = Field(
        default=True, description="Include metadata in exports"
    )
    pretty_json: bool = Field(default=True, description="Pretty print JSON exports")

    # ═══════════════════════════════════════════════════════════
    # Logging
    # ═══════════════════════════════════════════════════════════

    log_level: str = Field(default="INFO", description="Logging level")
    log_to_file: bool = Field(default=True, description="Enable file logging")
    log_to_console: bool = Field(default=True, description="Enable console logging")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format",
    )
    log_rotation: bool = Field(default=True, description="Enable log file rotation")
    log_max_size: int = Field(
        default=10_485_760,  # 10 MB
        description="Maximum log file size in bytes",
        ge=1_048_576,  # 1 MB minimum
    )
    log_backup_count: int = Field(
        default=5, description="Number of log backup files to keep", ge=1, le=20
    )

    # ═══════════════════════════════════════════════════════════
    # UI/CLI
    # ═══════════════════════════════════════════════════════════

    enable_colors: bool = Field(
        default=True, description="Enable colored output in CLI"
    )
    enable_progress_bars: bool = Field(default=True, description="Enable progress bars")
    page_size: int = Field(
        default=20, description="Number of items per page in lists", ge=5, le=100
    )

    # ═══════════════════════════════════════════════════════════
    # Development
    # ═══════════════════════════════════════════════════════════

    dev_mode: bool = Field(default=False, description="Enable development features")
    show_performance: bool = Field(
        default=False, description="Show performance metrics"
    )
    profile_code: bool = Field(default=False, description="Enable code profiling")

    # ═══════════════════════════════════════════════════════════
    # Pydantic Settings Configuration
    # ═══════════════════════════════════════════════════════════

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="SCHEDULE_DND_",
        case_sensitive=False,
        extra="ignore",
    )

    # ═══════════════════════════════════════════════════════════
    # Validators
    # ═══════════════════════════════════════════════════════════

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        """Validate log level."""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        value = value.upper()
        if value not in allowed_levels:
            raise ValueError(
                f"Invalid log level: {value}. Must be one of {allowed_levels}"
            )
        return value

    @field_validator("default_export_format")
    @classmethod
    def validate_export_format(cls, value: str) -> str:
        """Validate export format."""
        allowed_formats = ["json", "excel", "csv", "markdown", "html"]
        value = value.lower()
        if value not in allowed_formats:
            raise ValueError(
                f"Invalid export format: {value}. Must be one of {allowed_formats}"
            )
        return value

    @field_validator("base_dir", "data_dir", "output_dir", "log_dir")
    @classmethod
    def convert_to_path(cls, value: Any) -> Path:
        """Convert string paths to Path objects."""
        if isinstance(value, str):
            return Path(value)
        return value

    # ═══════════════════════════════════════════════════════════
    # Methods
    # ═══════════════════════════════════════════════════════════

    def create_directories(self) -> None:
        """Create all required directories if they don't exist."""
        directories = [
            self.data_dir,
            self.output_dir,
            self.log_dir,
        ]

        if self.enable_backup:
            directories.append(self.data_dir / "backups")

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == Environment.DEVELOPMENT or self.dev_mode

    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == Environment.PRODUCTION and not self.dev_mode

    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.environment == Environment.TESTING

    def get_log_file_path(self) -> Path:
        """Get the log file path."""
        return self.log_dir / f"{self.app_name.lower().replace(' ', '_')}.log"

    def get_schedule_file_path(self, year: int, month: int) -> Path:
        """
        Get the standard path for a schedule file.

        Args:
            year: Year of the schedule
            month: Month number (1-12)

        Returns:
            Path to the schedule file
        """
        filename = f"schedule_{year}_{month:02d}.json"
        return self.data_dir / filename

    def get_export_file_path(self, year: int, month: int, format_ext: str) -> Path:
        """
        Get the export file path.

        Args:
            year: Year of the schedule
            month: Month number (1-12)
            format_ext: File extension (json, xlsx, csv, etc.)

        Returns:
            Path to the export file
        """
        filename = f"schedule_{year}_{month:02d}.{format_ext}"
        return self.output_dir / filename

    def get_backup_file_path(
        self, original_path: Path, timestamp: Optional[str] = None
    ) -> Path:
        """
        Get backup file path for a given file.

        Args:
            original_path: Path to the original file
            timestamp: Optional timestamp string

        Returns:
            Path to the backup file
        """
        from datetime import datetime

        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        backup_dir = self.data_dir / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        stem = original_path.stem
        suffix = original_path.suffix
        backup_filename = f"{stem}_backup_{timestamp}{suffix}"

        return backup_dir / backup_filename

    def to_dict(self) -> dict[str, Any]:
        """Convert settings to dictionary."""
        return self.model_dump()

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"Settings(app_name='{self.app_name}', "
            f"version='{self.app_version}', "
            f"environment={self.environment.value})"
        )


# ═══════════════════════════════════════════════════════════
# Global Settings Instance
# ═══════════════════════════════════════════════════════════


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get the global settings instance (singleton pattern).

    Returns:
        Settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()
        _settings.create_directories()
    return _settings


def reset_settings() -> None:
    """Reset the global settings instance (useful for testing)."""
    global _settings
    _settings = None
