# Проверка

Дата: 2026-08-25. Стек: pytest 14, Streamlit AppTest, локальный HTTP.

## DoD

| Пункт | Вердикт | Улика |
|---|---|---|
| Три мира | GO | pytest `worlds == freelance, work, hobby` |
| Статусы | GO | YAML + смесь `now/queued/paused` сходится с pandas |
| Все открытые | GO | `open_by_world` + `count()` |
| Архив | GO | Adult Income `done`; визитка не в архиве, а в паузе |
| YAML → pandas → ClickHouse | GO | chDB MergeTree, `version()` не пустой, DuckDB нет в requirements |
| ORDER BY | GO | `(world, status, id)` + `LowCardinality` |
| xlsx | GO | PK-заголовок zip |
| Найм | GO | одна карточка `bi-seat` |
| SQL на экране | GO | AppTest грузит `app.py` без исключения |
| Статус-чарт | GO | fills = cyan / amber / pink, не серый и не белый |

## Команды

```
.venv/bin/pytest -q
# 14 passed
streamlit run app.py
```

## Ревью / рефакторинг

Сделано в этом ходе: палитра HUD и статусов — `board/constants.py` (Plotly + CSS custom properties). Снят мёртвый `open_counts`. Убран DuckDB. Временный Parquet живёт в `TemporaryDirectory`, не в git. Автозапуска нет.

Оставлено сознательно: HTML-триптих, а не Plotly-карточки (текст и ссылки читаются как документ). chDB вместо clickhouse-server, чтобы `pip install && streamlit run` работал без Docker.

## Итог

**GO** по данным, ClickHouse SQL, статусам визитки/Adult Income, приложению. Облачного URL нет — так и задумано.
