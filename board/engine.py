"""In-process ClickHouse (chDB). Same SQL dialect as a ClickHouse server."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
from chdb import session as chs

from . import queries


class ClickHouseEngine:
    """Owns a chDB Session and the Parquet snapshot used as the ingest source."""

    def __init__(self, sql_frame: pd.DataFrame) -> None:
        self._tmpdir = tempfile.TemporaryDirectory(prefix="personal-dashboard-ch-")
        self.parquet_path = Path(self._tmpdir.name) / "projects.parquet"
        sql_frame.to_parquet(self.parquet_path, index=False)
        # chDB EmbeddedServer is a process singleton. A second Session(path)
        # with a different directory fails; Session() is :memory: and shared.
        # CREATE OR REPLACE keeps Streamlit reruns and pytest loads idempotent.
        self.session = chs.Session()
        path = self.parquet_path.as_posix()
        self.session.query(queries.CREATE_PROJECTS.format(path=path))
        self.session.query(queries.CREATE_OPEN_VIEW)
        self.session.query(queries.CREATE_ARCHIVE_VIEW)

    def query_df(self, sql: str) -> pd.DataFrame:
        result = self.session.query(sql, "DataFrame")
        if isinstance(result, pd.DataFrame):
            return result
        return pd.DataFrame(result)

    def query_pretty(self, sql: str) -> str:
        return str(self.session.query(sql, "Pretty"))

    def version(self) -> str:
        frame = self.query_df(queries.SQL_VERSION)
        if frame.empty:
            return ""
        return str(frame.iloc[0]["clickhouse_version"])

    def close(self) -> None:
        try:
            self.session.close()
        finally:
            self._tmpdir.cleanup()
