#!/usr/bin/env python3
"""
Project Structure Setup Script for Schedule DND

This script creates the complete directory structure and placeholder files
for the Schedule DND application.

Author: DmitrTRC
Repository: https://github.com/DmitrTRC/schedule-dnd
"""

import sys
from pathlib import Path
from typing import Dict, List

# Color codes for terminal output
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_header() -> None:
    """Print script header."""
    print(f"\n{BLUE}{BOLD}{'=' * 70}{RESET}")
    print(f"{BLUE}{BOLD}Schedule DND - Project Structure Generator{RESET}")
    print(f"{BLUE}{BOLD}Author: DmitrTRC{RESET}")
    print(f"{BLUE}{BOLD}{'=' * 70}{RESET}\n")


def create_directory(path: Path) -> bool:
    """
    Create directory if it doesn't exist.

    Args:
        path: Path to directory

    Returns:
        True if directory was created, False if it already existed
    """
    if path.exists():
        print(f"{YELLOW}  ⊙ {path} (already exists){RESET}")
        return False

    path.mkdir(parents=True, exist_ok=True)
    print(f"{GREEN}  ✓ {path}{RESET}")
    return True


def create_file(path: Path, content: str = "") -> bool:
    """
    Create file with optional content if it doesn't exist.

    Args:
        path: Path to file
        content: Optional file content

    Returns:
        True if file was created, False if it already existed
    """
    if path.exists():
        print(f"{YELLOW}  ⊙ {path} (already exists){RESET}")
        return False

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"{GREEN}  ✓ {path}{RESET}")
    return True


def get_init_content(module_name: str) -> str:
    """
    Generate __init__.py content with docstring.

    Args:
        module_name: Name of the module

    Returns:
        Content for __init__.py file
    """
    return f'''"""
{module_name} module for Schedule DND application.

Author: DmitrTRC
"""

__all__: list[str] = []
'''


def get_placeholder_content(module_name: str, description: str) -> str:
    """
    Generate placeholder content for Python modules.

    Args:
        module_name: Name of the module
        description: Description of the module

    Returns:
        Placeholder content
    """
    return f'''"""
{description}

Author: DmitrTRC
"""

# TODO: Implement {module_name}
'''


def main() -> int:
    """
    Main function to create project structure.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    print_header()

    # Get project root (parent of scripts directory)
    project_root = Path(__file__).parent.parent
    print(f"Project root: {BOLD}{project_root}{RESET}\n")

    # Define directory structure
    directories = [
        # GitHub
        ".github/workflows",
        ".github/ISSUE_TEMPLATE",

        # Documentation
        "docs/api",
        "docs/architecture",

        # Source code - Domain Layer
        "src/schedule_dnd/domain",

        # Source code - Application Layer
        "src/schedule_dnd/application/services",

        # Source code - Infrastructure Layer
        "src/schedule_dnd/infrastructure/repositories",
        "src/schedule_dnd/infrastructure/exporters",
        "src/schedule_dnd/infrastructure/config",

        # Source code - Presentation Layer
        "src/schedule_dnd/presentation/cli/commands",

        # Tests
        "tests/unit/domain",
        "tests/unit/application",
        "tests/unit/infrastructure",
        "tests/unit/presentation",
        "tests/integration",
        "tests/fixtures",

        # Scripts
        "scripts",

        # Data directories
        "data",
        "output",
        "logs",
    ]

    # Define files with their content
    files: Dict[str, str] = {
        # Root level files
        ".env": "",  # Empty .env file

        # Source code __init__.py files
        "src/schedule_dnd/__init__.py": get_init_content("Schedule DND"),
        "src/schedule_dnd/__main__.py": get_placeholder_content(
            "main", "Entry point for Schedule DND application"
        ),

        # Domain Layer
        "src/schedule_dnd/domain/__init__.py": get_init_content("Domain"),
        "src/schedule_dnd/domain/models.py": get_placeholder_content(
            "models", "Domain models (Pydantic)"
        ),
        "src/schedule_dnd/domain/enums.py": "# Already created",
        "src/schedule_dnd/domain/exceptions.py": "# Already created",
        "src/schedule_dnd/domain/validators.py": get_placeholder_content(
            "validators", "Domain validation rules"
        ),
        "src/schedule_dnd/domain/constants.py": get_placeholder_content(
            "constants", "Domain constants"
        ),

        # Application Layer
        "src/schedule_dnd/application/__init__.py": get_init_content("Application"),
        "src/schedule_dnd/application/dto.py": get_placeholder_content(
            "dto", "Data Transfer Objects"
        ),
        "src/schedule_dnd/application/services/__init__.py": get_init_content("Services"),
        "src/schedule_dnd/application/services/schedule_service.py": get_placeholder_content(
            "schedule_service", "Schedule business logic service"
        ),
        "src/schedule_dnd/application/services/export_service.py": get_placeholder_content(
            "export_service", "Export orchestration service"
        ),

        # Infrastructure Layer
        "src/schedule_dnd/infrastructure/__init__.py": get_init_content("Infrastructure"),

        # Repositories
        "src/schedule_dnd/infrastructure/repositories/__init__.py": get_init_content("Repositories"),
        "src/schedule_dnd/infrastructure/repositories/base.py": get_placeholder_content(
            "base", "Abstract repository base class"
        ),
        "src/schedule_dnd/infrastructure/repositories/json_repository.py": get_placeholder_content(
            "json_repository", "JSON file repository implementation"
        ),

        # Exporters
        "src/schedule_dnd/infrastructure/exporters/__init__.py": get_init_content("Exporters"),
        "src/schedule_dnd/infrastructure/exporters/base.py": get_placeholder_content(
            "base", "Abstract exporter base class"
        ),
        "src/schedule_dnd/infrastructure/exporters/json_exporter.py": get_placeholder_content(
            "json_exporter", "JSON export implementation"
        ),
        "src/schedule_dnd/infrastructure/exporters/excel_exporter.py": get_placeholder_content(
            "excel_exporter", "Excel export implementation"
        ),
        "src/schedule_dnd/infrastructure/exporters/csv_exporter.py": get_placeholder_content(
            "csv_exporter", "CSV export implementation"
        ),
        "src/schedule_dnd/infrastructure/exporters/markdown_exporter.py": get_placeholder_content(
            "markdown_exporter", "Markdown export implementation"
        ),
        "src/schedule_dnd/infrastructure/exporters/html_exporter.py": get_placeholder_content(
            "html_exporter", "HTML export implementation"
        ),
        "src/schedule_dnd/infrastructure/exporters/factory.py": get_placeholder_content(
            "factory", "Exporter factory"
        ),

        # Config
        "src/schedule_dnd/infrastructure/config/__init__.py": get_init_content("Config"),
        "src/schedule_dnd/infrastructure/config/settings.py": get_placeholder_content(
            "settings", "Application settings (Pydantic Settings)"
        ),

        # Presentation Layer
        "src/schedule_dnd/presentation/__init__.py": get_init_content("Presentation"),
        "src/schedule_dnd/presentation/cli/__init__.py": get_init_content("CLI"),
        "src/schedule_dnd/presentation/cli/app.py": get_placeholder_content(
            "app", "Main CLI application class"
        ),
        "src/schedule_dnd/presentation/cli/formatters.py": get_placeholder_content(
            "formatters", "Output formatters for CLI"
        ),

        # CLI Commands
        "src/schedule_dnd/presentation/cli/commands/__init__.py": get_init_content("Commands"),
        "src/schedule_dnd/presentation/cli/commands/create.py": get_placeholder_content(
            "create", "Create new schedule command"
        ),
        "src/schedule_dnd/presentation/cli/commands/load.py": get_placeholder_content(
            "load", "Load existing schedule command"
        ),
        "src/schedule_dnd/presentation/cli/commands/export.py": get_placeholder_content(
            "export", "Export schedule command"
        ),
        "src/schedule_dnd/presentation/cli/commands/base.py": get_placeholder_content(
            "base", "Base command class"
        ),

        # Tests
        "tests/__init__.py": "",
        "tests/conftest.py": get_placeholder_content(
            "conftest", "Pytest configuration and fixtures"
        ),

        # Unit tests
        "tests/unit/__init__.py": "",
        "tests/unit/domain/__init__.py": "",
        "tests/unit/domain/test_models.py": get_placeholder_content(
            "test_models", "Unit tests for domain models"
        ),
        "tests/unit/domain/test_enums.py": get_placeholder_content(
            "test_enums", "Unit tests for domain enums"
        ),
        "tests/unit/domain/test_validators.py": get_placeholder_content(
            "test_validators", "Unit tests for validators"
        ),

        "tests/unit/application/__init__.py": "",
        "tests/unit/application/test_schedule_service.py": get_placeholder_content(
            "test_schedule_service", "Unit tests for schedule service"
        ),
        "tests/unit/application/test_export_service.py": get_placeholder_content(
            "test_export_service", "Unit tests for export service"
        ),

        "tests/unit/infrastructure/__init__.py": "",
        "tests/unit/infrastructure/test_repositories.py": get_placeholder_content(
            "test_repositories", "Unit tests for repositories"
        ),
        "tests/unit/infrastructure/test_exporters.py": get_placeholder_content(
            "test_exporters", "Unit tests for exporters"
        ),

        "tests/unit/presentation/__init__.py": "",
        "tests/unit/presentation/test_cli.py": get_placeholder_content(
            "test_cli", "Unit tests for CLI"
        ),

        # Integration tests
        "tests/integration/__init__.py": "",
        "tests/integration/test_end_to_end.py": get_placeholder_content(
            "test_end_to_end", "End-to-end integration tests"
        ),

        # Test fixtures
        "tests/fixtures/sample_schedule.json": "{}",

        # Documentation
        "docs/architecture.md": "# Architecture\n\nTODO: Document architecture\n",
        "docs/api.md": "# API Documentation\n\nTODO: Document API\n",
        "docs/contributing.md": "# Contributing Guide\n\nTODO: Document contribution guidelines\n",

        # GitHub
        ".github/ISSUE_TEMPLATE/bug_report.md": "# Bug Report\n\nTODO: Create template\n",
        ".github/ISSUE_TEMPLATE/feature_request.md": "# Feature Request\n\nTODO: Create template\n",
        ".github/pull_request_template.md": "# Pull Request\n\nTODO: Create template\n",

        # Scripts
        "scripts/lint.sh": "#!/bin/bash\n# TODO: Add linting script\n",
        "scripts/test.sh": "#!/bin/bash\n# TODO: Add testing script\n",

        # Keep directories
        "data/.gitkeep": "",
        "output/.gitkeep": "",
        "logs/.gitkeep": "",
    }

    # Create directories
    print(f"{BOLD}Creating directories...{RESET}")
    created_dirs = 0
    existing_dirs = 0

    for directory in directories:
        dir_path = project_root / directory
        if create_directory(dir_path):
            created_dirs += 1
        else:
            existing_dirs += 1

    print(f"\n{BOLD}Summary:{RESET} {GREEN}{created_dirs} created{RESET}, {YELLOW}{existing_dirs} existed{RESET}\n")

    # Create files
    print(f"{BOLD}Creating files...{RESET}")
    created_files = 0
    existing_files = 0

    for filepath, content in files.items():
        file_path = project_root / filepath
        if create_file(file_path, content):
            created_files += 1
        else:
            existing_files += 1

    print(f"\n{BOLD}Summary:{RESET} {GREEN}{created_files} created{RESET}, {YELLOW}{existing_files} existed{RESET}\n")

    # Final summary
    print(f"{BLUE}{BOLD}{'=' * 70}{RESET}")
    print(f"{GREEN}{BOLD}✓ Project structure created successfully!{RESET}")
    print(f"{BLUE}{BOLD}{'=' * 70}{RESET}\n")

    print(f"{BOLD}Next steps:{RESET}")
    print(f"  1. Review the created structure")
    print(f"  2. Copy configuration files to project root:")
    print(f"     - pyproject.toml")
    print(f"     - .gitignore")
    print(f"     - .env.example")
    print(f"     - Makefile")
    print(f"     - .pre-commit-config.yaml")
    print(f"  3. Run: {GREEN}poetry install{RESET}")
    print(f"  4. Run: {GREEN}pre-commit install{RESET}")
    print(f"  5. Start implementing modules!\n")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Interrupted by user{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}{BOLD}Error: {e}{RESET}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
