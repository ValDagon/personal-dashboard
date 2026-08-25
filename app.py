from __future__ import annotations

from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

from board import queries
from board.constants import WORLD_LABEL
from board.export import open_projects_xlsx
from board.load import load_board
from board.render import render_board

ROOT = Path(__file__).resolve().parent
CSS = (ROOT / "assets" / "style.css").read_text(encoding="utf-8")
WORLD_ORDER = ["freelance", "work", "hobby"]
SCENE = "#0B1220"
INK = "#E8F1FF"
RULE = "#1A3D52"
MUTED = "#8AA0B8"
WORLD_COLORS = {
    "freelance": "#FFB14A",
    "work": "#3EC4FF",
    "hobby": "#FF6BB5",
}

st.set_page_config(
    page_title="Три мира",
    page_icon="▣",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;600&display=swap" rel="stylesheet">
    """,
    unsafe_allow_html=True,
)
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

@st.cache_resource
def _cached_board(mtime: float):
    return load_board()


board = _cached_board((ROOT / "data" / "projects.yaml").stat().st_mtime)
html = render_board(board)
if hasattr(st, "html"):
    st.html(html)
else:
    st.markdown(html, unsafe_allow_html=True)

mix = board.open_mix()
labels = [WORLD_LABEL[w] for w in WORLD_ORDER]
colors = [WORLD_COLORS[w] for w in WORLD_ORDER]


def _mix_value(world: str, col: str) -> int:
    hit = mix.loc[mix["world"] == world, col]
    return int(hit.iloc[0]) if not hit.empty else 0


open_x = [_mix_value(world, "open_n") for world in WORLD_ORDER]
fig_open = go.Figure(
    go.Bar(
        x=open_x,
        y=labels,
        orientation="h",
        marker_color=colors,
        hovertemplate="%{y}: %{x}<extra></extra>",
    )
)
fig_open.update_layout(
    title="Открытые карточки",
    margin=dict(l=8, r=8, t=40, b=8),
    height=200,
    paper_bgcolor=SCENE,
    plot_bgcolor=SCENE,
    font=dict(family="IBM Plex Sans, sans-serif", color=INK, size=13),
    xaxis=dict(title="штук", dtick=1, gridcolor=RULE),
    yaxis=dict(title=""),
    showlegend=False,
)

fig_status = go.Figure()
status_cols = [
    ("now_n", "сейчас", INK),
    ("queued_n", "очередь", WORLD_COLORS["freelance"]),
    ("paused_n", "пауза", MUTED),
]
for col, name, color in status_cols:
    fig_status.add_trace(
        go.Bar(
            name=name,
            x=labels,
            y=[_mix_value(world, col) for world in WORLD_ORDER],
            marker_color=color,
            hovertemplate="%{x} · " + name + ": %{y}<extra></extra>",
        )
    )
fig_status.update_layout(
    title="Открытые по статусу",
    barmode="stack",
    margin=dict(l=8, r=8, t=40, b=8),
    height=220,
    paper_bgcolor=SCENE,
    plot_bgcolor=SCENE,
    font=dict(family="IBM Plex Sans, sans-serif", color=INK, size=13),
    yaxis=dict(title="штук", dtick=1, gridcolor=RULE),
    xaxis=dict(title=""),
    legend=dict(orientation="h", y=-0.2),
)

left, right = st.columns(2)
with left:
    st.plotly_chart(fig_open, width="stretch")
with right:
    st.plotly_chart(fig_status, width="stretch")

st.download_button(
    label="Скачать открытые в Excel",
    data=open_projects_xlsx(board.open_frame()),
    file_name="personal-dashboard-open.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

with st.expander("SQL, которым считаются цифры"):
    st.caption(
        f"ClickHouse {board.engine.version()} внутри процесса (chDB). "
        "Отдельный сервер для клона репозитория не нужен."
    )
    for title, sql in queries.INSPECTOR:
        st.markdown(f"**{title}**")
        st.code(sql.strip(), language="sql")
        st.dataframe(board.query(sql), hide_index=True, width="stretch")

st.caption("YAML → pandas → ClickHouse MergeTree → Streamlit. Без облачного хостинга этой доски.")
