"""
Home page - main page of the PWA.

Displays list of available schedules with actions (view, export, delete).

Author: DmitrTRC
Version: 0.1.0 (PoC)
"""

import logging
from typing import Any

import flet as ft

from schedule_dnd.presentation.web.adapters.service_adapter import FletServiceAdapter

logger = logging.getLogger(__name__)


class HomePage:
    """
    Home page component.

    Displays:
    - Welcome message
    - List of available schedules
    - Quick actions (create new schedule)
    """

    def __init__(self, page: ft.Page, adapter: FletServiceAdapter) -> None:
        """
        Initialize home page.

        Args:
            page: Flet page instance
            adapter: Service adapter for data operations
        """
        self.page = page
        self.adapter = adapter
        self.schedules: list[dict[str, Any]] = []
        self.schedules_list = ft.Column(spacing=10)

        logger.info("HomePage initialized")

    def build(self) -> ft.Column:
        """
        Build home page UI.

        Returns:
            Column widget with page content
        """
        return ft.Column(
            controls=[
                # Header
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "📅 Управление графиками ДНД",
                                size=28,
                                weight="bold",
                                color=ft.colors.BLUE_700,
                            ),
                            ft.Text(
                                "Система управления графиками патрульных дежурств",
                                size=16,
                                color=ft.colors.GREY_700,
                            ),
                        ],
                        spacing=5,
                    ),
                    padding=ft.padding.only(bottom=20),
                ),
                # Action buttons
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            "➕ Создать график",
                            icon=ft.icons.ADD_CIRCLE_OUTLINE,
                            on_click=self._create_schedule,
                            bgcolor=ft.colors.BLUE_700,
                            color=ft.colors.WHITE,
                        ),
                        ft.ElevatedButton(
                            "🔄 Обновить",
                            icon=ft.icons.REFRESH,
                            on_click=self._load_schedules,
                        ),
                    ],
                    spacing=10,
                ),
                ft.Divider(),
                # Schedules list
                ft.Text(
                    "Доступные графики:",
                    size=20,
                    weight="bold",
                ),
                self.schedules_list,
            ],
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def did_mount(self) -> None:
        """Called when page is mounted."""
        self._load_schedules(None)

    def _load_schedules(self, e: ft.ControlEvent | None) -> None:
        """
        Load schedules from service.

        Args:
            e: Event (unused, but required for button callback)
        """
        try:
            logger.info("Loading schedules...")
            self.schedules = self.adapter.list_schedules()
            logger.info(f"Loaded {len(self.schedules)} schedules")

            # Clear existing list
            self.schedules_list.controls.clear()

            if not self.schedules:
                # Show empty state
                self.schedules_list.controls.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(
                                    ft.icons.CALENDAR_MONTH_OUTLINED,
                                    size=64,
                                    color=ft.colors.GREY_400,
                                ),
                                ft.Text(
                                    "Графиков пока нет",
                                    size=18,
                                    color=ft.colors.GREY_600,
                                ),
                                ft.Text(
                                    "Создайте первый график!",
                                    size=14,
                                    color=ft.colors.GREY_500,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=10,
                        ),
                        alignment=ft.alignment.center,
                        padding=40,
                    )
                )
            else:
                # Display schedule cards
                for schedule in self.schedules:
                    card = self._create_schedule_card(schedule)
                    self.schedules_list.controls.append(card)

            self.page.update()

        except Exception as ex:
            logger.error(f"Error loading schedules: {ex}")
            self._show_error(f"Ошибка загрузки: {ex}")

    def _create_schedule_card(self, schedule: dict[str, Any]) -> ft.Card:
        """
        Create a card for a schedule.

        Args:
            schedule: Schedule data

        Returns:
            Card widget
        """
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        # Header
                        ft.Row(
                            [
                                ft.Icon(
                                    ft.icons.CALENDAR_MONTH,
                                    color=ft.colors.BLUE_700,
                                ),
                                ft.Column(
                                    [
                                        ft.Text(
                                            f"{schedule['month']} {schedule['year']}",
                                            size=18,
                                            weight="bold",
                                        ),
                                        ft.Text(
                                            f"Создан: {schedule['created_at']}",
                                            size=12,
                                            color=ft.colors.GREY_600,
                                        ),
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                            ],
                            spacing=10,
                        ),
                        # Stats
                        ft.Row(
                            [
                                ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Text(
                                                str(schedule["total_shifts"]),
                                                size=24,
                                                weight="bold",
                                                color=ft.colors.BLUE_700,
                                            ),
                                            ft.Text(
                                                "смен",
                                                size=12,
                                                color=ft.colors.GREY_600,
                                            ),
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        spacing=2,
                                    ),
                                    bgcolor=ft.colors.BLUE_50,
                                    border_radius=8,
                                    padding=10,
                                ),
                                ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Text(
                                                str(schedule["unit_count"]),
                                                size=24,
                                                weight="bold",
                                                color=ft.colors.GREEN_700,
                                            ),
                                            ft.Text(
                                                "юнитов",
                                                size=12,
                                                color=ft.colors.GREY_600,
                                            ),
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        spacing=2,
                                    ),
                                    bgcolor=ft.colors.GREEN_50,
                                    border_radius=8,
                                    padding=10,
                                ),
                            ],
                            spacing=10,
                        ),
                        ft.Divider(),
                        # Actions
                        ft.Row(
                            [
                                ft.TextButton(
                                    "📊 Просмотр",
                                    icon=ft.icons.VISIBILITY,
                                    on_click=lambda e, s=schedule: self._view_schedule(
                                        s
                                    ),
                                ),
                                ft.TextButton(
                                    "📤 Экспорт",
                                    icon=ft.icons.FILE_DOWNLOAD,
                                    on_click=lambda e, s=schedule: self._export_schedule(
                                        s
                                    ),
                                ),
                                ft.TextButton(
                                    "🗑️ Удалить",
                                    icon=ft.icons.DELETE,
                                    on_click=lambda e, s=schedule: self._delete_schedule(
                                        s
                                    ),
                                ),
                            ],
                            spacing=5,
                        ),
                    ],
                    spacing=10,
                ),
                padding=15,
            ),
            elevation=2,
        )

    def _create_schedule(self, e: ft.ControlEvent) -> None:
        """Navigate to create schedule page."""
        self._show_info("Функция создания графика будет добавлена в следующей версии")

    def _view_schedule(self, schedule: dict[str, Any]) -> None:
        """View schedule details."""
        self._show_info(
            f"Просмотр графика: {schedule['month']} {schedule['year']}\n"
            f"(Будет реализовано в следующей версии)"
        )

    def _export_schedule(self, schedule: dict[str, Any]) -> None:
        """Export schedule."""

        # Show export format selection dialog
        def export_format_selected(format_name: str):
            dlg.open = False
            self.page.update()

            try:
                result = self.adapter.export_schedule(schedule["filename"], format_name)

                if result["success"]:
                    self._show_success(
                        f"График экспортирован в {format_name.upper()}\n"
                        f"Файл: {result['output_path']}"
                    )
                else:
                    self._show_error(f"Ошибка экспорта: {result['error']}")

            except Exception as ex:
                logger.error(f"Export error: {ex}")
                self._show_error(f"Ошибка: {ex}")

        dlg = ft.AlertDialog(
            title=ft.Text("Выберите формат экспорта"),
            content=ft.Column(
                [
                    ft.TextButton(
                        "JSON", on_click=lambda e: export_format_selected("json")
                    ),
                    ft.TextButton(
                        "Excel", on_click=lambda e: export_format_selected("excel")
                    ),
                    ft.TextButton(
                        "CSV", on_click=lambda e: export_format_selected("csv")
                    ),
                    ft.TextButton(
                        "Markdown",
                        on_click=lambda e: export_format_selected("markdown"),
                    ),
                    ft.TextButton(
                        "HTML", on_click=lambda e: export_format_selected("html")
                    ),
                ],
                tight=True,
            ),
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def _delete_schedule(self, schedule: dict[str, Any]) -> None:
        """Delete schedule with confirmation."""

        def confirm_delete(e):
            dlg.open = False
            self.page.update()

            try:
                result = self.adapter.delete_schedule(schedule["filename"])
                if result:
                    self._show_success("График удален")
                    self._load_schedules(None)
                else:
                    self._show_error("Не удалось удалить график")
            except Exception as ex:
                logger.error(f"Delete error: {ex}")
                self._show_error(f"Ошибка: {ex}")

        def cancel_delete(e):
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Подтверждение"),
            content=ft.Text(f"Удалить график {schedule['month']} {schedule['year']}?"),
            actions=[
                ft.TextButton("Отмена", on_click=cancel_delete),
                ft.TextButton("Удалить", on_click=confirm_delete),
            ],
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    # ═══════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════

    def _show_info(self, message: str) -> None:
        """Show info snackbar."""
        self.page.snack_bar = ft.SnackBar(
            ft.Text(message),
            bgcolor=ft.colors.BLUE_700,
        )
        self.page.snack_bar.open = True
        self.page.update()

    def _show_success(self, message: str) -> None:
        """Show success snackbar."""
        self.page.snack_bar = ft.SnackBar(
            ft.Text(message),
            bgcolor=ft.colors.GREEN_700,
        )
        self.page.snack_bar.open = True
        self.page.update()

    def _show_error(self, message: str) -> None:
        """Show error snackbar."""
        self.page.snack_bar = ft.SnackBar(
            ft.Text(message),
            bgcolor=ft.colors.RED_700,
        )
        self.page.snack_bar.open = True
        self.page.update()
