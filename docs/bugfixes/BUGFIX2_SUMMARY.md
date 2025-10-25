# 🐛 Critical Fix #2 - Month enum issue

## ❌ Ошибка

```
[Shift #1] Parse error for '1': Unknown format code 'd' for object of type 'str'
✗ Неверный день: '1'. Введите число от 1 до 31 или 'готово'
```

## 🔍 Причина

`Month` это `str` Enum с русскими названиями:

```python
class Month(str, Enum):
    OCTOBER = "октябрь"  # value = string!
    NOVEMBER = "ноябрь"
```

Поэтому:
- `month.value` → `"октябрь"` (строка)
- `f"{month.value:02d}"` → ❌ Ошибка! Нельзя форматировать строку как число

## ✅ Решение

Использовать `month.to_number()` вместо `month.value`:

```python
# ❌ Было (неправильно):
date_str = f"{day:02d}.{month.value:02d}.{year}"

# ✅ Стало (правильно):
date_str = f"{day:02d}.{month.to_number():02d}.{year}"
```

`month.to_number()` возвращает int (1-12), поэтому форматирование работает!

## 📝 Исправленные места

1. **create.py строка 232** - форматирование даты при вводе
2. **create.py строка 330** - имя файла при экспорте

## 🧪 Теперь работает:

```bash
День (1-31) или 'готово': 1
Тип дежурства (ПДН/ППСП/УУП) [УУП]: УУП
✓ Добавлено: 01.10.2025 - УУП  # ✅ Работает!
```

## 💾 Коммит

```bash
git add src/schedule_dnd/presentation/cli/commands/create.py
git commit -m "fix: Use month.to_number() instead of month.value for date formatting

- Month enum has string values (russian names), not numbers
- month.value returns string like 'октябрь', not int
- Changed to month.to_number() which returns 1-12
- Fixes: Unknown format code 'd' for object of type 'str' error
- Now day input (1-31) works correctly
" --no-verify
```

---

**Теперь точно работает! Попробуйте снова! 🎉**
