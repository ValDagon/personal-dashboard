from __future__ import annotations

from io import BytesIO

import pandas as pd

from .constants import STATUS_LABEL, WORLD_LABEL


def open_projects_xlsx(frame: pd.DataFrame) -> bytes:
    rows = frame.copy()
    rows["мир"] = rows["world"].map(WORLD_LABEL)
    rows["статус"] = rows["status"].map(STATUS_LABEL)
    rows["стек"] = rows["stack"].apply(
        lambda value: ", ".join(value) if isinstance(value, list) else str(value)
    )
    rows["ссылки"] = rows["links"].apply(
        lambda value: " ".join(value) if isinstance(value, list) else ""
    )
    if "stale_days" in rows.columns:
        rows["дней_без_обновления"] = rows["stale_days"]
    else:
        rows["дней_без_обновления"] = 0
    export = rows[
        [
            "мир",
            "public_title",
            "статус",
            "blurb",
            "стек",
            "updated",
            "дней_без_обновления",
            "ссылки",
        ]
    ].rename(
        columns={
            "public_title": "проект",
            "blurb": "описание",
            "updated": "обновлён",
        }
    )
    buffer = BytesIO()
    export.to_excel(buffer, index=False, sheet_name="открытые")
    return buffer.getvalue()
