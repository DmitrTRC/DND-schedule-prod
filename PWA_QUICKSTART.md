# 🚀 Запуск PWA модуля (Proof of Concept)

Быстрая инструкция по запуску PWA версии Schedule DND.

## 📦 Установка

```bash
# 1. Установить Flet
poetry add flet

# 2. Обновить зависимости
poetry install
```

## 🚀 Запуск

```bash
# Активировать виртуальное окружение
poetry shell

# Запустить PWA
poetry run schedule-dnd-web

# ИЛИ напрямую:
python src/schedule_dnd/presentation/web/app.py
```

## 🌐 Открыть в браузере

```
http://localhost:8080
```

## ✅ Что работает в PoC

- ✅ Список графиков из `/data` директории
- ✅ Экспорт в 5 форматов (JSON/Excel/CSV/Markdown/HTML)
- ✅ Удаление графиков
- ✅ Material Design UI
- ✅ Responsive (desktop + mobile)

## 📖 Подробная документация

См. `src/schedule_dnd/presentation/web/README.md`

## 🐛 Troubleshooting

### Порт 8080 занят?

```bash
# Измените порт в app.py (строка с ft.app(..., port=8080))
ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8090)
```

### Графики не отображаются?

- Проверь, что в `/data` есть JSON файлы графиков
- Создай график через CLI: `poetry run schedule-dnd create`

### Ошибка импорта Flet?

```bash
poetry add flet
poetry install
```

---

**Следующий шаг**: Тестируй PoC и дай фидбек! 🎯
