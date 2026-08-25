from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

from board.charts import open_by_status_figure, open_by_world_figure
from board.constants import (
    ARCHIVE_STATUSES,
    HUD_INK,
    HUD_PANEL,
    HUD_SCENE,
    OPEN_STATUSES,
    STATUS_COLORS,
    WORLD_COLORS,
    WORLDS,
    css_custom_properties,
)
from board.export import open_projects_xlsx
from board.load import load_board
from board import queries

ROOT = Path(__file__).resolve().parent.parent
YAML = ROOT / "data" / "projects.yaml"
REQ = ROOT / "requirements.txt"


def test_three_worlds_and_statuses() -> None:
    board = load_board(YAML)
    worlds = set(board.frame["world"])
    assert worlds == set(WORLDS)
    assert set(board.frame["status"]) <= set(OPEN_STATUSES + ARCHIVE_STATUSES)


def test_second_load_does_not_collide_on_projects_table() -> None:
    first = load_board(YAML)
    second = load_board(YAML)
    assert len(first.frame) == len(second.frame) == 10
    assert first.engine.version()
    assert second.engine.version()
    first.engine.close()
    second.engine.close()


def test_clickhouse_views_partition_open_and_archive() -> None:
    board = load_board(YAML)
    open_n = int(board.query(queries.SQL_OPEN_TOTAL).iloc[0]["n"])
    archive_n = int(board.query(queries.SQL_ARCHIVE_TOTAL).iloc[0]["n"])
    assert open_n + archive_n == len(board.frame)
    assert open_n == int(board.frame["is_open"].sum())
    version = board.engine.version()
    assert version
    assert "." in version


def test_clickhouse_mix_matches_pandas() -> None:
    board = load_board(YAML)
    mix = board.open_mix()
    assert set(mix["world"]) <= set(WORLDS)
    for _, row in mix.iterrows():
        world = str(row["world"])
        pandas_open = board.for_world(world, open_only=True)
        assert int(row["open_n"]) == len(pandas_open)
        assert int(row["now_n"]) == int((pandas_open["status"] == "now").sum())
        assert int(row["now_n"]) + int(row["queued_n"]) + int(row["paused_n"]) == int(
            row["open_n"]
        )


def test_clickhouse_order_by_is_low_cardinality_first() -> None:
    ddl = str(board_create_statement())
    assert "ORDER BY (world, status, id)" in ddl
    assert "LowCardinality(String)" in ddl
    assert "MergeTree" in ddl


def board_create_statement() -> str:
    board = load_board(YAML)
    pretty = board.engine.query_pretty("SHOW CREATE TABLE projects")
    return pretty


def test_runtime_is_clickhouse_not_duckdb() -> None:
    text = REQ.read_text(encoding="utf-8").lower()
    assert "chdb" in text
    assert "duckdb" not in text
    load_src = (ROOT / "board" / "load.py").read_text(encoding="utf-8")
    assert "duckdb" not in load_src


def test_public_copy_has_no_private_leaks() -> None:
    public = "\n".join(
        p.read_text(encoding="utf-8").lower()
        for p in (
            ROOT / "README.md",
            ROOT / "app.py",
            ROOT / "board" / "render.py",
            YAML,
        )
    )
    banned = (
        "crystal",
        "obsidian",
        "agents.md",
        "spiridonova",
        "tdata",
        ".session",
        "bot_token",
        "launchagent",
    )
    for word in banned:
        assert word not in public
    titles = set(board_titles())
    assert "HR-бот" in titles
    assert "Relomap" in titles
    assert "Личная визитка" in titles
    assert not any("crystal" in title.lower() for title in titles)


def board_titles() -> list[str]:
    return list(load_board(YAML).frame["public_title"])


def test_work_world_is_honest_seat_only() -> None:
    board = load_board(YAML)
    work = board.for_world("work")
    assert len(work) == 1
    assert bool(work.iloc[0]["hire_private"]) is True
    assert work.iloc[0]["status"] == "now"


def test_adult_case_is_hobby_archive() -> None:
    board = load_board(YAML)
    row = board.frame[board.frame["id"] == "adult-income-case"].iloc[0]
    assert row["world"] == "hobby"
    assert row["status"] == "done"
    assert bool(row["is_archive"]) is True


def test_personal_card_is_paused() -> None:
    board = load_board(YAML)
    row = board.frame[board.frame["id"] == "personal-card"].iloc[0]
    assert row["status"] == "paused"
    assert bool(row["is_open"]) is True


def test_stale_days_are_non_negative() -> None:
    board = load_board(YAML)
    assert (board.frame["stale_days"] >= 0).all()


def test_xlsx_export_not_empty() -> None:
    board = load_board(YAML)
    payload = open_projects_xlsx(board.open_frame())
    assert payload[:2] == b"PK"
    assert len(payload) > 100


def test_status_palette_is_neon_not_gray() -> None:
    assert STATUS_COLORS == {
        "now": "#3DFF8A",
        "queued": "#FFB14A",
        "paused": "#FF6BB5",
    }
    assert WORLD_COLORS == {
        "freelance": "#FFB14A",
        "work": "#FF6BB5",
        "hobby": "#3EC4FF",
    }
    fig = open_by_status_figure(
        pd.DataFrame(
            {
                "world": ["freelance", "work", "hobby"],
                "now_n": [0, 1, 1],
                "queued_n": [2, 0, 0],
                "paused_n": [0, 0, 1],
            }
        )
    )
    fills = [trace.marker.color for trace in fig.data]
    assert fills == ["#3DFF8A", "#FFB14A", "#FF6BB5"]
    names = [trace.name for trace in fig.data]
    assert names == ["сейчас", "очередь", "пауза"]
    banned = ("#8a93a0", "#8A93A0", "#8AA0B8", "#E8F1FF", "#1a2332", "#1A2332")
    for hex_ in banned:
        assert hex_.lower() not in [str(fill).lower() for fill in fills]
    charts_src = (ROOT / "board" / "charts.py").read_text(encoding="utf-8")
    assert "STATUS_COLORS" in charts_src
    for hex_ in ("#8a93a0", "#8AA0B8"):
        assert hex_.lower() not in charts_src.lower()
    tokens = css_custom_properties()
    for hex_ in STATUS_COLORS.values():
        assert hex_ in tokens
    css = (ROOT / "assets" / "style.css").read_text(encoding="utf-8")
    assert "var(--status-now)" in css
    assert "var(--status-queued)" in css
    assert "var(--status-paused)" in css
    world_fig = open_by_world_figure(
        pd.DataFrame(
            {
                "world": ["freelance", "work", "hobby"],
                "open_n": [2, 1, 2],
            }
        )
    )
    assert list(world_fig.data[0].marker.color) == [
        "#FFB14A",
        "#FF6BB5",
        "#3EC4FF",
    ]
    theme = (ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8")
    assert HUD_SCENE in theme
    assert HUD_PANEL in theme
    assert HUD_INK in theme
    app_src = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "css_custom_properties" in app_src
    assert "WORLD_COLORS =" not in app_src


def test_streamlit_app_runs() -> None:
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    assert not at.exception
    html_el = at.main.children[2]
    assert "Персональный дашборд" in html_el.body
    assert 'class="desk"' in html_el.body
    at.run()
    assert not at.exception
