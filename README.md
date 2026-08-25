# Three worlds

Personal ops board for a Junior BI analyst: **Freelance · Work · Hobby** as three separate lives on one screen.

> Spec is in review (`docs/10-product-spec.md`). The app UI is not shipped yet. This README is the hiring-facing envelope.

## Why this exists

Resume shows tools. This repo shows **how those tools organize real work**: whole projects, not task soup; three worlds that never collapse into one feed; an archive you can ignore until you need it.

Stack matches the day job, not a side-product frontend: Python, pandas, SQL (DuckDB), Excel export, Streamlit as the BI web surface (same family as the `adult-bi` case). Not Next.js.

## What you will see (layout)

```
+--------------------------- /now ticker ---------------------------+
| Freelance: …     Work: …     Hobby: …              updated: date  |
+------------------+-------------------+---------------------------+
| FREELANCE        | WORK              | HOBBY                     |
| open cards       | open cards        | open cards                |
| [archive folded] | [archive folded]  | [archive folded]          |
+------------------+-------------------+---------------------------+
```

On a phone the worlds become tabs. Cards stay whole projects. Closed work lives in a collapsed archive per world.

### Status legend

| RU | Meaning |
|---|---|
| сейчас | in motion |
| очередь | next, not started |
| пауза | parked |
| сделано | finished (self) |
| сдано клиенту | handed to a client |

## Stack

| Layer | Choice | Why |
|---|---|---|
| Cards SSOT | YAML | git-diffable, no database secrets |
| Tables | pandas | hiring stack |
| SQL | DuckDB over that table | show SQL without a warehouse |
| UI | Streamlit + custom CSS | BI web app; Streamlit already in the BI case |
| Charts | Plotly | optional counts, no vanity KPIs |
| Export | openpyxl `.xlsx` | how analysts actually deliver |
| Not used | Next.js, Tableau Cloud, ClickHouse Cloud | out of hiring-stack / privacy / disk |

## Data model

`data/projects.yaml` — one document per project:

- `id`, `world` (`freelance` \| `work` \| `hobby`)
- `status` (see legend)
- `public_title`, `blurb` (safe for GitHub)
- `stack` (list of tools)
- `updated` (ISO date)
- `links` (public URLs only)
- `confidence` (`high` \| `medium` \| `low`)

Private client names do not belong in this file.

## How to run (after implement)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Tests (data layer): `pytest`

## Architecture

YAML → pandas → DuckDB views (`open_by_world`, `archive_by_world`) → Streamlit triptych. Details-on-demand on card click. See `docs/10-product-spec.md`.

## Screenshots

_Placeholder — add after the first UI gate. Desktop 1280 and mobile 375._

## License

MIT. See `LICENSE`.

## Topics (when the GitHub repo is created)

`python` `pandas` `duckdb` `streamlit` `plotly` `business-intelligence` `portfolio` `personal-dashboard`
