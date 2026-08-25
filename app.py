from __future__ import annotations

from pathlib import Path

import streamlit as st

from board import queries
from board.charts import open_by_status_figure, open_by_world_figure
from board.constants import css_custom_properties
from board.export import open_projects_xlsx
from board.load import load_board
from board.render import render_board

ROOT = Path(__file__).resolve().parent
CSS = (ROOT / "assets" / "style.css").read_text(encoding="utf-8")

st.set_page_config(
    page_title="Персональный дашборд",
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
st.markdown(f"<style>{CSS}\n{css_custom_properties()}</style>", unsafe_allow_html=True)


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
left, right = st.columns(2)
with left:
    st.plotly_chart(open_by_world_figure(mix), width="stretch")
with right:
    st.plotly_chart(open_by_status_figure(mix), width="stretch")

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
