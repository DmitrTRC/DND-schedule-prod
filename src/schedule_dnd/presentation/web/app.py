"""
Flet PWA application entry point.

This is the main entry point for the Schedule DND Progressive Web App.
It initializes the Flet application and sets up routing between pages.

Author: DmitrTRC
Version: 0.1.0 (PoC)
"""

import logging
from pathlib import Path

import flet as ft

from schedule_dnd.application.services.export_service import ExportService
from schedule_dnd.application.services.schedule_service import ScheduleService
from schedule_dnd.infrastructure.config.settings import get_settings
from schedule_dnd.infrastructure.exporters.factory import ExporterFactory
from schedule_dnd.infrastructure.repositories.json_repository import (
    JSONScheduleRepository,
)
from schedule_dnd.presentation.web.adapters.service_adapter import FletServiceAdapter
from schedule_dnd.presentation.web.pages.home import HomePage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main(page: ft.Page) -> None:
    """
    Main application entry point.

    Args:
        page: Flet page instance
    """
    # ═══════════════════════════════════════════════════════════
    # Page Configuration
    # ═══════════════════════════════════════════════════════════
    page.title = "Schedule DND - Управление графиками ДНД"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    # Responsive window sizing
    if page.platform in [ft.PagePlatform.ANDROID, ft.PagePlatform.IOS]:
        page.window_width = 400
        page.window_height = 800
    else:
        page.window_width = 1200
        page.window_height = 800

    logger.info(f"Starting Schedule DND PWA on platform: {page.platform}")

    # ═══════════════════════════════════════════════════════════
    # Initialize Services (Clean Architecture)
    # ═══════════════════════════════════════════════════════════
    settings = get_settings()
    repository = JSONScheduleRepository(data_dir=settings.data_dir)
    schedule_service = ScheduleService(repository=repository)

    exporter_factory = ExporterFactory(output_dir=settings.output_dir)
    export_service = ExportService(
        repository=repository, exporter_factory=exporter_factory
    )

    # Create adapter for Flet integration
    adapter = FletServiceAdapter(
        schedule_service=schedule_service,
        export_service=export_service,
    )

    logger.info("Services initialized successfully")

    # ═══════════════════════════════════════════════════════════
    # Routing
    # ═══════════════════════════════════════════════════════════
    def route_change(e: ft.RouteChangeEvent) -> None:
        """Handle route changes."""
        page.views.clear()

        # Always add home page as base
        if page.route == "/" or page.route == "/home":
            home_page = HomePage(page, adapter)
            page.views.append(
                ft.View(
                    "/",
                    controls=[home_page.build()],
                    appbar=create_app_bar(),
                )
            )
        # Future: Add more routes
        # elif page.route == "/create":
        #     create_page = CreatePage(page, adapter)
        #     page.views.append(ft.View("/create", [create_page.build()]))

        page.update()

    def view_pop(e: ft.ViewPopEvent) -> None:
        """Handle back button."""
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # ═══════════════════════════════════════════════════════════
    # Initial Route
    # ═══════════════════════════════════════════════════════════
    page.go("/")


def create_app_bar() -> ft.AppBar:
    """
    Create application bar.

    Returns:
        AppBar widget
    """
    return ft.AppBar(
        title=ft.Text("Schedule DND", size=20, weight="bold"),
        center_title=False,
        bgcolor=ft.colors.BLUE_700,
        actions=[
            ft.IconButton(
                icon=ft.icons.BRIGHTNESS_6,
                tooltip="Переключить тему",
                # on_click will be added later
            ),
        ],
    )


def start_app() -> None:
    """Start the Flet application."""
    logger.info("=" * 60)
    logger.info("Schedule DND PWA - Starting")
    logger.info("=" * 60)

    # Start Flet app
    # view=ft.WEB_BROWSER for PWA mode
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8080)


if __name__ == "__main__":
    start_app()
