from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import yaml

from .constants import ARCHIVE_STATUSES, OPEN_STATUSES, STATUS_LABEL, STATUSES, WORLDS
from .engine import ClickHouseEngine
from . import queries

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_YAML = ROOT / "data" / "projects.yaml"


@dataclass
class BoardData:
    updated: str
    frame: pd.DataFrame
    engine: ClickHouseEngine

    def query(self, sql: str) -> pd.DataFrame:
        return self.engine.query_df(sql)

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
        status = str(pick.iloc[0]["status"])
        return f"{title} · {STATUS_LABEL[status]}"

    def open_mix(self) -> pd.DataFrame:
        return self.query(queries.SQL_OPEN_MIX)

    def mix_for(self, world: str) -> dict[str, float]:
        mix = self.open_mix()
        hit = mix.loc[mix["world"] == world]
        if hit.empty:
            return {"now_n": 0, "queued_n": 0, "paused_n": 0, "open_n": 0, "avg_stale_days": 0}
        row = hit.iloc[0]
        return {
            "now_n": int(row["now_n"]),
            "queued_n": int(row["queued_n"]),
            "paused_n": int(row["paused_n"]),
            "open_n": int(row["open_n"]),
            "avg_stale_days": float(row["avg_stale_days"]),
        }


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


def _sql_frame(frame: pd.DataFrame) -> pd.DataFrame:
    sql = pd.DataFrame(
        {
            "id": frame["id"].astype(str),
            "world": frame["world"].astype(str),
            "status": frame["status"].astype(str),
            "public_title": frame["public_title"].astype(str),
            "blurb": frame["blurb"].astype(str),
            "stack": frame["stack"].map(lambda value: ", ".join(value)),
            "links": frame["links"].map(lambda value: " ".join(value)),
            "updated": frame["updated"].astype(str),
            "is_open": frame["is_open"].astype("uint8"),
            "is_archive": frame["is_archive"].astype("uint8"),
            "hire_private": frame["hire_private"].astype("uint8"),
        }
    )
    return sql


def load_board(path: Path | None = None) -> BoardData:
    yaml_path = path or DEFAULT_YAML
    raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    updated = str(raw.get("updated", ""))
    projects = raw.get("projects") or []
    frame = _normalize(pd.DataFrame(projects))
    engine = ClickHouseEngine(_sql_frame(frame))
    stale = engine.query_df(queries.SQL_STALE)
    frame = frame.merge(stale, on="id", how="left")
    frame["stale_days"] = frame["stale_days"].fillna(0).astype(int)
    return BoardData(updated=updated, frame=frame, engine=engine)
