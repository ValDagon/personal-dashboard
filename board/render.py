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


def _stale_label(days: object) -> str:
    try:
        n = int(days)
    except (TypeError, ValueError):
        return ""
    if n <= 0:
        return "сегодня"
    if n == 1:
        return "1 день назад"
    if n in (2, 3, 4):
        return f"{n} дня назад"
    return f"{n} дн. назад"


def _card(row: pd.Series) -> str:
    status = str(row["status"])
    hire_note = ""
    if bool(row.get("hire_private")):
        hire_note = (
            '<p class="honest">Проекты найма не публикую. '
            "Это не пустая колонка, а сознательный пробел.</p>"
        )
    stale = _stale_label(row.get("stale_days"))
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
  <p class="meta">обновлён {_esc(row["updated"])} · { _esc(stale) }</p>
</article>
"""


def _lane(board: BoardData, world: str) -> str:
    label = WORLD_LABEL[world]
    open_rows = board.for_world(world, open_only=True)
    archive_rows = board.for_world(world, open_only=False)
    mix = board.mix_for(world)
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

    mix_line = (
        f"{mix['open_n']} открыто · "
        f"{mix['now_n']} сейчас · "
        f"{mix['queued_n']} очередь · "
        f"{mix['paused_n']} пауза"
    )
    return f"""
<section class="lane lane-{_esc(world)}" id="lane-{_esc(world)}">
  <header class="lane-head">
    <div>
      <h2>{_esc(label)}</h2>
      <p class="mix">{_esc(mix_line)}</p>
    </div>
  </header>
  <div class="lane-body">
    {"".join(blocks)}
    {archive_html}
  </div>
</section>
"""


def _mix_strip(board: BoardData) -> str:
    cells = []
    for world in ("freelance", "work", "hobby"):
        mix = board.mix_for(world)
        stale = mix["avg_stale_days"]
        stale_txt = "—" if mix["open_n"] == 0 else f"{stale:g} дн. в среднем"
        cells.append(
            f"""
            <div class="mix-cell mix-{_esc(world)}">
              <span class="mix-k">{_esc(WORLD_LABEL[world])}</span>
              <span class="mix-n">{mix['open_n']}</span>
              <span class="mix-d">открытых · { _esc(stale_txt) }</span>
            </div>
            """
        )
    return f'<section class="mix-strip" aria-label="Нагрузка по мирам">{"".join(cells)}</section>'


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
    <p class="lede">Фриланс, работа и хобби рядом, но не в одной куче. Карточка = целый проект. Закрытое спрятано в архив мира. Числа считаются ClickHouse SQL по YAML, не руками.</p>
  </header>
  <section class="now" aria-label="Сейчас по мирам">
    {now_cells}
    <p class="now-stamp">снимок данных {_esc(stamp)}</p>
  </section>
  {_mix_strip(board)}
  <div class="legend" aria-label="Статусы">
    <span><i class="lg lg-now"></i>сейчас</span>
    <span><i class="lg lg-queued"></i>очередь</span>
    <span><i class="lg lg-paused"></i>пауза</span>
    <span><i class="lg lg-done"></i>архив</span>
  </div>
  <div class="world-switch" role="tablist" aria-label="Мир">
    <a class="tab tab-freelance" href="#lane-freelance">Фриланс</a>
    <a class="tab tab-work" href="#lane-work">Работа</a>
    <a class="tab tab-hobby" href="#lane-hobby">Хобби</a>
  </div>
  <div class="triptych">
    {lanes}
  </div>
</div>
"""
