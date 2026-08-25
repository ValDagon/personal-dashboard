# AGENTS.md — personal-dashboard

> Сначала этот файл → `docs/PROGRESS.md`.

## 0.1 NOW

> **Сейчас:** релизный полиш HUD. Статус-чарт cyan/amber/pink из `board/constants.py`. Выкладка только GitHub, без автозапуска.
> **Не делать:** Next.js-оболочка; облачный деплой доски; выдуманные кейсы найма; четвёртая колонка; LaunchAgent.

| | |
|---|---|
| **Live** | Python · pandas · ClickHouse (chDB) · Streamlit · Plotly |
| **Проверка** | `pytest` · `streamlit run app.py` |

## 1. Миссия

Публичная доска трёх миров (фриланс / работа / хобби) на BI-стеке найма.

## 2. Старт

1. §0.1 и хвост `docs/PROGRESS.md`.
2. UI: отличимый CSS, IBM Plex, токены из `assets/style.css`.
3. Не отправлять человека «напиши код сам».

## 3. Карта

| Путь | Зачем |
|---|---|
| `app.py` | экран |
| `board/constants.py` | палитра HUD и статусов |
| `board/` | YAML, ClickHouse, HTML, xlsx |
| `data/projects.yaml` | SSOT карточек |
| `docs/10-product-spec.md` | спека |
| `tests/` | слой данных |

## 4. Инварианты

1. Нет секретов.
2. Остаёмся в этом корне.
3. Три мира не сливать.
4. Публичный текст без внутренних имён ОС и скрытых заказчиков.
