"""
Schedule DND Application - Entry Point

Author: DmitrTRC
"""

import sys
from pathlib import Path

# Ensure src directory is in path
sys.path.insert(0, str(Path(__file__).parent.parent))


def main() -> int:
    """
    Main entry point for Schedule DND application.

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        # Import here to avoid circular imports
        from schedule_dnd.presentation.cli.app import create_app

        app = create_app()
        return app.run()

    except KeyboardInterrupt:
        print("\n\nПрервано пользователем.")
        return 130
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        if "--debug" in sys.argv:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
