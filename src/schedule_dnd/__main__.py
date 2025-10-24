"""
Schedule DND Application - Entry Point

Author: DmitrTRC
"""

import os
import sys
from pathlib import Path

# Ensure src directory is in path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Force UTF-8 encoding for Mac terminals
if sys.platform == "darwin":  # Mac OS
    os.environ["LANG"] = "en_US.UTF-8"
    os.environ["LC_ALL"] = "en_US.UTF-8"
    os.environ["PYTHONIOENCODING"] = "utf-8"


def main() -> int:
    """
    Main entry point for Schedule DND application.

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        # Setup logging first
        from schedule_dnd.infrastructure.logging import setup_logging

        setup_logging()

        import logging

        logger = logging.getLogger(__name__)
        logger.info("Application starting...")
        logger.info(f"Platform: {sys.platform}")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Default encoding: {sys.getdefaultencoding()}")
        logger.info(f"stdin encoding: {sys.stdin.encoding}")
        logger.info(f"stdout encoding: {sys.stdout.encoding}")

        # Import here to avoid circular imports
        from schedule_dnd.presentation.cli.app import create_app

        app = create_app()
        exit_code = app.run()

        logger.info(f"Application finished with exit code: {exit_code}")
        return exit_code

    except KeyboardInterrupt:
        print("\n\nПрервано пользователем.")
        return 130
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        if (
            "--debug" in sys.argv
            or os.environ.get("SCHEDULE_DND_DEBUG", "").lower() == "true"
        ):
            import traceback

            traceback.print_exc()

        # Try to log the error
        try:
            import logging

            logger = logging.getLogger(__name__)
            logger.exception("Critical error in main()")
        except:
            pass

        return 1


if __name__ == "__main__":
    sys.exit(main())
