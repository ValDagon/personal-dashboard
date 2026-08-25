# Research synthesis · personal / BI life dashboards

Date checked: 2026-08-25. Not a bibliography dump — keep / adapt / reject vs locked core (3 worlds, whole-project cards, all open items, 5 statuses, collapsible archive).

## Discover (skills / MCP)

| Item | Verdict |
|---|---|
| Vault: `crystal-bootstrap-repo`, `crystal-specify`, `obsidian-visual` (not used for UI) | KEEP process |
| [streamlit/agent-skills](https://www.skills.sh/streamlit/agent-skills) `developing-with-streamlit` (~2.7k installs) | **KEEP after gate** — official Streamlit pack |
| `improving-streamlit-design`, `building-streamlit-dashboards` | KEEP with hallmark |
| Evidence.dev + SQL-markdown | REJECT as runtime (weak card/triptych UX); ADAPT narrative README |
| Next.js / Relomap skills | REJECT for this repo |
| Obsidian MCP | REJECT — this is not the vault app |
| Tableau MCP | NO-GO — Desktop only |

## Academic / HCI

| Source | Takeaway | Vs core |
|---|---|---|
| Li, Dey, Forlizzi, CHI 2010 — [stage model](https://personalinformatics.ianli.com/lab/model) | Preparation → Collection → Integration → Reflection → Action; multi-facet lives; barriers cascade | **KEEP** three facets = three worlds; YAML = collection; dashboard = reflection. **REJECT** quantified-self sensors |
| Li thesis — questions: Status, History, Goal, Discrepancy | Status-at-a-glance + history (archive) | **ADAPT** `/now` = Status; archive = History; skip Goal bars unless real numbers |
| Shneiderman 1996 — [Eyes Have It](http://www.cs.umd.edu/~ben/papers/Shneiderman1996eyes.pdf) | Overview, zoom/filter, details-on-demand | **KEEP** ticker + triptych + card drill-in |

## Blogs / PKM

| Source | Takeaway | Vs core |
|---|---|---|
| [Sivers /now](https://sive.rs/now2) | What you'd tell a friend; date updated; not a CV | **KEEP** header strip, one line per world |
| Tiago Forte PARA | Projects vs areas vs archive | **ADAPT** archive collapse; **REJECT** merging worlds into one Projects folder on screen |
| Life-dashboard blogs (Streamlit + habits + bank) | Centralize everything | **REJECT** health/finance scope creep |

## GitHub / tools

| Source | Takeaway | Vs core |
|---|---|---|
| [Evidence.dev](https://github.com/evidence-dev/evidence) | SQL-in-md static BI, Vercel-friendly | ADAPT DuckDB SQL views; REJECT as shell |
| [jeremy6680/personal-warehouse-dashboard](https://github.com/jeremy6680/personal-warehouse-dashboard) | Evidence + dbt + warehouse | REJECT infra weight for a card board |
| Streamlit portfolio guides | One-click live URL for hiring managers | **KEEP** Streamlit Cloud later |
| LifeLens / VisionBoard2026 | Habits, scores, mock data | REJECT fake scores (hallmark invented-metrics) |
| DEV comparison Streamlit vs Evidence vs Dash vs Superset | Streamlit = interactive Python; Evidence = narrative SQL | **KEEP** Streamlit for cards; SQL still via DuckDB |

## Hiring-manager practices (BI portfolio)

Three E's (access / navigate / consume in <30s). README states business question, method, insight — here the «business question» is *how this analyst runs three lives*. Live URL > notebooks. Excel export shows deliverable format of the day job.

## Organic extensions (allowed)

1. `/now` ticker (Sivers) — three lines, not a fourth world.
2. Case-study drill-in (stack badges, public link only).
3. Honest counts: open cards per world (computed, not invented %).
4. xlsx export of the open set.
5. Optional later: Tableau Public twin of the same YAML grain.

## Ignored on purpose

Quantified self, Notion clones, Kanban plugins, AI chat in the dashboard, merging worlds, Crystal OS as column 4, Relomap Next.js rewrite.
