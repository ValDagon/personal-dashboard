from __future__ import annotations

from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

from board.constants import WORLD_LABEL
from board.export import open_projects_xlsx
from board.load import load_board
from board.render import render_board

ROOT = Path(__file__).resolve().parent
CSS = (ROOT / "assets" / "style.css").read_text(encoding="utf-8")

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

board = load_board()
html = render_board(board)
if hasattr(st, "html"):
    st.html(html)
else:
    st.markdown(html, unsafe_allow_html=True)

counts = board.open_counts()
label_map = WORLD_LABEL
ordered = ["freelance", "work", "hobby"]
y = [label_map[w] for w in ordered]
x = []
for world in ordered:
    hit = counts.loc[counts["world"] == world, "open_count"]
    x.append(int(hit.iloc[0]) if not hit.empty else 0)
colors = ["#c45c26", "#2f5c8f", "#3d6b4f"]

fig = go.Figure(
    go.Bar(
        x=x,
        y=y,
        orientation="h",
        marker_color=colors,
        hovertemplate="%{y}: %{x}<extra></extra>",
    )
)
fig.update_layout(
    title="Открытые проекты по мирам",
    margin=dict(l=8, r=8, t=40, b=8),
    height=180,
    paper_bgcolor="#eef1f4",
    plot_bgcolor="#eef1f4",
    font=dict(family="IBM Plex Sans, sans-serif", color="#1a2332", size=13),
    xaxis=dict(title="штук", dtick=1, gridcolor="#c5ccd6"),
    yaxis=dict(title=""),
    showlegend=False,
)
st.plotly_chart(fig, width="stretch")

st.download_button(
    label="Скачать открытые в Excel",
    data=open_projects_xlsx(board.open_frame()),
    file_name="three-worlds-open.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

st.caption("YAML → pandas → DuckDB. Локальный запуск, без облачного хостинга этой доски.")
