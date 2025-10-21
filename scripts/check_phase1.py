#!/usr/bin/env python3
"""
Phase 1 completion checker for Schedule DND project.

This script verifies that all Phase 1 components are properly created.
Author: DmitrTRC
"""

import sys
from pathlib import Path
from typing import List, Tuple

# Color codes
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_header() -> None:
    """Print checker header."""
    print(f"\n{BLUE}{BOLD}{'=' * 70}{RESET}")
    print(f"{BLUE}{BOLD}Phase 1 Completion Checker - Domain Layer{RESET}")
    print(f"{BLUE}{BOLD}Author: DmitrTRC{RESET}")
    print(f"{BLUE}{BOLD}{'=' * 70}{RESET}\n")


def check_file_exists(filepath: Path) -> Tuple[bool, str]:
    """
    Check if file exists and has content.

    Returns:
        Tuple of (exists, status_message)
    """
    if not filepath.exists():
        return False, f"{RED}✗ Missing{RESET}"

    if filepath.stat().st_size == 0:
        return False, f"{YELLOW}⚠ Empty{RESET}"

    return True, f"{GREEN}✓ OK{RESET}"


def check_domain_layer(project_root: Path) -> Tuple[int, int]:
    """
    Check domain layer files.

    Returns:
        Tuple of (passed, total)
    """
    print(f"{BOLD}Domain Layer:{RESET}")

    files = [
        "src/schedule_dnd/__init__.py",
        "src/schedule_dnd/domain/__init__.py",
        "src/schedule_dnd/domain/models.py",
        "src/schedule_dnd/domain/enums.py",
        "src/schedule_dnd/domain/exceptions.py",
        "src/schedule_dnd/domain/validators.py",
        "src/schedule_dnd/domain/constants.py",
    ]

    passed = 0
    total = len(files)

    for filepath in files:
        full_path = project_root / filepath
        exists, status = check_file_exists(full_path)
        print(f"  {status} {filepath}")
        if exists:
            passed += 1

    print()
    return passed, total


def check_tests(project_root: Path) -> Tuple[int, int]:
    """
    Check test files.

    Returns:
        Tuple of (passed, total)
    """
    print(f"{BOLD}Tests:{RESET}")

    files = [
        "tests/__init__.py",
        "tests/conftest.py",
        "tests/unit/domain/__init__.py",
        "tests/unit/domain/test_models.py",
        "tests/unit/domain/test_enums.py",
        "tests/unit/domain/test_validators.py",
    ]

    passed = 0
    total = len(files)

    for filepath in files:
        full_path = project_root / filepath
        exists, status = check_file_exists(full_path)
        print(f"  {status} {filepath}")
        if exists:
            passed += 1

    print()
    return passed, total


def check_configuration(project_root: Path) -> Tuple[int, int]:
    """
    Check configuration files.

    Returns:
        Tuple of (passed, total)
    """
    print(f"{BOLD}Configuration:{RESET}")

    files = [
        "pyproject.toml",
        ".gitignore",
        ".env.example",
        "Makefile",
        ".pre-commit-config.yaml",
        ".github/workflows/ci.yml",
    ]

    passed = 0
    total = len(files)

    for filepath in files:
        full_path = project_root / filepath
        exists, status = check_file_exists(full_path)
        print(f"  {status} {filepath}")
        if exists:
            passed += 1

    print()
    return passed, total


def check_scripts(project_root: Path) -> Tuple[int, int]:
    """
    Check script files.

    Returns:
        Tuple of (passed, total)
    """
    print(f"{BOLD}Scripts:{RESET}")

    files = [
        "scripts/setup_project_structure.py",
        "scripts/setup.sh",
        "scripts/copy_config_files.sh",
        "scripts/check_phase1.py",
        "activate_env.sh",
    ]

    passed = 0
    total = len(files)

    for filepath in files:
        full_path = project_root / filepath
        exists, status = check_file_exists(full_path)
        print(f"  {status} {filepath}")
        if exists:
            passed += 1

    print()
    return passed, total


def check_documentation(project_root: Path) -> Tuple[int, int]:
    """
    Check documentation files.

    Returns:
        Tuple of (passed, total)
    """
    print(f"{BOLD}Documentation:{RESET}")

    files = [
        "README.md",
        "SETUP_INSTRUCTIONS.md",
        "scripts/README.md",
    ]

    passed = 0
    total = len(files)

    for filepath in files:
        full_path = project_root / filepath
        exists, status = check_file_exists(full_path)
        print(f"  {status} {filepath}")
        if exists:
            passed += 1

    print()
    return passed, total


def run_tests(project_root: Path) -> bool:
    """
    Try to run tests.

    Returns:
        True if tests can be run
    """
    print(f"{BOLD}Running Tests:{RESET}")

    try:
        import subprocess

        result = subprocess.run(
            ["poetry", "run", "pytest", "tests/unit/domain/", "-v", "--tb=short"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            print(f"  {GREEN}✓ Tests passed{RESET}")
            # Count passed tests
            output = result.stdout
            if "passed" in output:
                print(
                    f"  {BLUE}{output.split('passed')[0].strip().split()[-1]} tests passed{RESET}"
                )
            return True
        else:
            print(f"  {YELLOW}⚠ Some tests failed{RESET}")
            print(f"  {YELLOW}Run 'make test' for details{RESET}")
            return False

    except FileNotFoundError:
        print(f"  {YELLOW}⚠ Poetry not found, skipping test run{RESET}")
        return False
    except subprocess.TimeoutExpired:
        print(f"  {YELLOW}⚠ Tests timed out{RESET}")
        return False
    except Exception as e:
        print(f"  {YELLOW}⚠ Could not run tests: {e}{RESET}")
        return False

    print()


def main() -> int:
    """
    Main checker function.

    Returns:
        Exit code
    """
    print_header()

    project_root = Path(__file__).parent.parent
    print(f"Project root: {BOLD}{project_root}{RESET}\n")

    # Run all checks
    results = []
    results.append(check_domain_layer(project_root))
    results.append(check_tests(project_root))
    results.append(check_configuration(project_root))
    results.append(check_scripts(project_root))
    results.append(check_documentation(project_root))

    # Calculate totals
    total_passed = sum(r[0] for r in results)
    total_files = sum(r[1] for r in results)

    # Print summary
    print(f"{BLUE}{BOLD}{'=' * 70}{RESET}")
    print(f"{BOLD}Summary:{RESET}")
    print(f"  Files checked: {total_files}")
    print(f"  {GREEN}Passed: {total_passed}{RESET}")
    print(f"  {RED}Failed: {total_files - total_passed}{RESET}")

    percentage = (total_passed / total_files * 100) if total_files > 0 else 0
    print(f"  Completion: {percentage:.1f}%")
    print()

    # Run tests if all files are present
    if total_passed == total_files:
        print(f"{GREEN}✓ All Phase 1 files are present!{RESET}\n")
        tests_passed = run_tests(project_root)
        print()

        if tests_passed:
            print(f"{GREEN}{BOLD}🎉 Phase 1 is COMPLETE!{RESET}")
            print(f"\n{BOLD}Next steps:{RESET}")
            print(f"  1. Review the domain models")
            print(f"  2. Run full test suite: {GREEN}make test{RESET}")
            print(f"  3. Check code quality: {GREEN}make lint{RESET}")
            print(f"  4. Ready for Phase 2!\n")
            return 0
        else:
            print(f"{YELLOW}Phase 1 files complete, but tests need attention{RESET}\n")
            return 1
    else:
        print(f"{RED}✗ Phase 1 is INCOMPLETE{RESET}")
        print(f"\n{BOLD}Missing files:{RESET}")
        print(f"  Run: {GREEN}python3 scripts/setup_project_structure.py{RESET}")
        print(f"  Or:  {GREEN}./scripts/setup.sh{RESET}\n")
        return 1


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
