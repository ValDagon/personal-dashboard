from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import duckdb
import pandas as pd
import yaml

from .constants import ARCHIVE_STATUSES, OPEN_STATUSES, STATUSES, WORLDS

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_YAML = ROOT / "data" / "projects.yaml"


@dataclass(frozen=True)
class BoardData:
    updated: str
    frame: pd.DataFrame
    connection: duckdb.DuckDBPyConnection

    def open_frame(self) -> pd.DataFrame:
        return self.frame[self.frame["is_open"]].copy()

    def archive_frame(self) -> pd.DataFrame:
        return self.frame[~self.frame["is_open"]].copy()

    def for_world(self, world: str, *, open_only: bool | None = None) -> pd.DataFrame:
        part = self.frame[self.frame["world"] == world]
        if open_only is True:
            part = part[part["is_open"]]
        elif open_only is False:
            part = part[~part["is_open"]]
        return part.copy()

    def now_line(self, world: str) -> str:
        rows = self.for_world(world, open_only=True)
        if rows.empty:
            return "нет открытых"
        now = rows[rows["status"] == "now"]
        pick = now if not now.empty else rows
        title = str(pick.iloc[0]["public_title"])
        return title

    def open_counts(self) -> pd.DataFrame:
        return self.connection.execute(
            """
            SELECT world, COUNT(*) AS open_count
            FROM open_by_world
            GROUP BY world
            ORDER BY world
            """
        ).df()


def _normalize(frame: pd.DataFrame) -> pd.DataFrame:
    need = {"id", "world", "status", "public_title", "blurb", "stack", "updated"}
    missing = need - set(frame.columns)
    if missing:
        raise ValueError(f"нет полей: {sorted(missing)}")

    out = frame.copy()
    if "links" not in out.columns:
        out["links"] = [[] for _ in range(len(out))]
    if "hire_private" not in out.columns:
        out["hire_private"] = False
    else:
        out["hire_private"] = out["hire_private"].fillna(False).astype(bool)

    out["world"] = out["world"].astype(str)
    out["status"] = out["status"].astype(str)
    out["public_title"] = out["public_title"].astype(str)
    out["blurb"] = out["blurb"].astype(str)
    out["updated"] = out["updated"].astype(str)
    out["stack"] = out["stack"].apply(
        lambda value: list(value) if isinstance(value, list) else []
    )
    out["links"] = out["links"].apply(
        lambda value: [str(item) for item in value] if isinstance(value, list) else []
    )

    bad_world = sorted(set(out["world"]) - set(WORLDS))
    if bad_world:
        raise ValueError(f"неизвестный мир: {bad_world}")
    bad_status = sorted(set(out["status"]) - set(STATUSES))
    if bad_status:
        raise ValueError(f"неизвестный статус: {bad_status}")

    out["is_open"] = out["status"].isin(OPEN_STATUSES)
    out["is_archive"] = out["status"].isin(ARCHIVE_STATUSES)
    return out.reset_index(drop=True)


def load_board(path: Path | None = None) -> BoardData:
    yaml_path = path or DEFAULT_YAML
    raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    updated = str(raw.get("updated", ""))
    projects = raw.get("projects") or []
    frame = _normalize(pd.DataFrame(projects))

    connection = duckdb.connect(":memory:")
    connection.register("projects", frame)
    connection.execute(
        """
        CREATE VIEW open_by_world AS
        SELECT *
        FROM projects
        WHERE is_open
        """
    )
    connection.execute(
        """
        CREATE VIEW archive_by_world AS
        SELECT *
        FROM projects
        WHERE is_archive
        """
    )
    return BoardData(updated=updated, frame=frame, connection=connection)
