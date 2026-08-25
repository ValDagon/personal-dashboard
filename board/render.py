from __future__ import annotations

import html
from datetime import date

import pandas as pd

from .constants import OPEN_ORDER, STATUS_LABEL, WORLD_LABEL
from .load import BoardData


def _esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def _stack(chips: list[str]) -> str:
    if not chips:
        return ""
    parts = "".join(f'<span class="chip">{_esc(item)}</span>' for item in chips)
    return f'<div class="chips">{parts}</div>'


def _links(urls: list[str]) -> str:
    if not urls:
        return ""
    items = "".join(
        f'<a class="ext" href="{_esc(url)}" rel="noopener noreferrer" target="_blank">{_esc(url)}</a>'
        for url in urls
    )
    return f'<div class="links">{items}</div>'


def _card(row: pd.Series) -> str:
    status = str(row["status"])
    hire_note = ""
    if bool(row.get("hire_private")):
        hire_note = (
            '<p class="honest">Проекты найма не публикую. '
            "Это не пустая колонка, а сознательный пробел.</p>"
        )
    return f"""
<article class="card status-{_esc(status)}">
  <header class="card-head">
    <h3>{_esc(row["public_title"])}</h3>
    <span class="pill">{_esc(STATUS_LABEL[status])}</span>
  </header>
  <p class="blurb">{_esc(row["blurb"])}</p>
  {hire_note}
  {_stack(list(row["stack"]))}
  {_links(list(row["links"]))}
  <p class="meta">обновлён {_esc(row["updated"])}</p>
</article>
"""


def _lane(board: BoardData, world: str) -> str:
    label = WORLD_LABEL[world]
    open_rows = board.for_world(world, open_only=True)
    archive_rows = board.for_world(world, open_only=False)
    blocks: list[str] = []
    for status in OPEN_ORDER:
        chunk = open_rows[open_rows["status"] == status]
        for _, row in chunk.iterrows():
            blocks.append(_card(row))
    if open_rows.empty:
        blocks.append(
            '<p class="empty">Открытых проектов в этом мире нет.</p>'
        )

    archive_html = ""
    if not archive_rows.empty:
        inner = "".join(_card(row) for _, row in archive_rows.iterrows())
        archive_html = f"""
<details class="archive">
  <summary>Архив · {len(archive_rows)}</summary>
  {inner}
</details>
"""

    count = int(open_rows.shape[0])
    return f"""
<section class="lane lane-{_esc(world)}" id="lane-{_esc(world)}">
  <header class="lane-head">
    <h2>{_esc(label)}</h2>
    <span class="count">{count} открыто</span>
  </header>
  <div class="lane-body">
    {"".join(blocks)}
    {archive_html}
  </div>
</section>
"""


def render_board(board: BoardData) -> str:
    now_cells = "".join(
        f"""
        <div class="now-cell now-{_esc(world)}">
          <span class="now-k">{_esc(WORLD_LABEL[world])}</span>
          <span class="now-v">{_esc(board.now_line(world))}</span>
        </div>
        """
        for world in ("freelance", "work", "hobby")
    )
    lanes = "".join(_lane(board, world) for world in ("freelance", "work", "hobby"))
    stamp = board.updated or date.today().isoformat()
    return f"""
<div class="desk">
  <header class="mast">
    <p class="kicker">три мира · одна доска</p>
    <h1>Сейчас</h1>
    <p class="lede">Фриланс, работа и хобби рядом, но не в одной куче. Карточка = целый проект. Закрытое спрятано в архив мира.</p>
  </header>
  <section class="now" aria-label="Сейчас по мирам">
    {now_cells}
    <p class="now-stamp">данные {_esc(stamp)}</p>
  </section>
  <div class="world-switch" role="tablist" aria-label="Мир">
    <a class="tab" href="#lane-freelance">Фриланс</a>
    <a class="tab" href="#lane-work">Работа</a>
    <a class="tab" href="#lane-hobby">Хобби</a>
  </div>
  <div class="triptych">
    {lanes}
  </div>
</div>
"""
