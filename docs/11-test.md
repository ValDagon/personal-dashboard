# Проверка

Дата: 2026-08-25. Стек: pytest + локальный Streamlit.

## DoD

| Пункт | Вердикт | Улика |
|---|---|---|
| Три мира | GO | `pytest` — `worlds == freelance, work, hobby` |
| Статусы | GO | YAML + `STATUS_LABEL` |
| Все открытые | GO | представление `open_by_world` |
| Архив | GO | `done` и `delivered` в `archive_by_world` |
| YAML → pandas → DuckDB | GO | 6 тестов зелёные |
| xlsx | GO | файл начинается с PK (zip/xlsx) |
| Найм без выдуманных кейсов | GO | одна карточка `bi-seat`, `hire_private` |
| Adult Income в хобби | GO | `adult-income-case.world == hobby` |
| Нет скрытых имён в YAML | GO | бан-лист в тесте |
| README / запуск | GO | README на русском |
| Узкий экран | partial GO | CSS вкладки + `overflow-x: clip`; живой просмотр 375px — отдельно |

## Команды

```
pytest
streamlit run app.py
```

`pytest`: 6 passed.

## Итог

**GO** по слою данных и каркасу UI. Облачного URL нет — так и задумано.
