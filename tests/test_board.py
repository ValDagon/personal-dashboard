from pathlib import Path

from board.constants import ARCHIVE_STATUSES, OPEN_STATUSES, WORLDS
from board.export import open_projects_xlsx
from board.load import load_board

ROOT = Path(__file__).resolve().parent.parent
YAML = ROOT / "data" / "projects.yaml"


def test_three_worlds_and_statuses() -> None:
    board = load_board(YAML)
    worlds = set(board.frame["world"])
    assert worlds == set(WORLDS)
    assert set(board.frame["status"]) <= set(OPEN_STATUSES + ARCHIVE_STATUSES)


def test_duckdb_views() -> None:
    board = load_board(YAML)
    open_n = int(board.connection.execute("SELECT COUNT(*) FROM open_by_world").fetchone()[0])
    archive_n = int(
        board.connection.execute("SELECT COUNT(*) FROM archive_by_world").fetchone()[0]
    )
    assert open_n + archive_n == len(board.frame)
    assert open_n == int(board.frame["is_open"].sum())


def test_public_copy_has_no_private_leaks() -> None:
    text = YAML.read_text(encoding="utf-8").lower()
    banned = (
        "crystal",
        "obsidian",
        "agents.md",
        "spiridonova",
        "tdata",
        ".session",
        "bot_token",
    )
    for word in banned:
        assert word not in text
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


def test_adult_case_is_hobby() -> None:
    board = load_board(YAML)
    row = board.frame[board.frame["id"] == "adult-income-case"].iloc[0]
    assert row["world"] == "hobby"


def test_xlsx_export_not_empty() -> None:
    board = load_board(YAML)
    payload = open_projects_xlsx(board.open_frame())
    assert payload[:2] == b"PK"
    assert len(payload) > 100
