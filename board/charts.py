"""Plotly figures. Colors come only from board.constants."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from .constants import (
    HUD_INK,
    HUD_RULE,
    HUD_SCENE,
    STATUS_COLORS,
    STATUS_LABEL,
    WORLD_COLORS,
    WORLD_LABEL,
    WORLD_ORDER,
)

_FONT = dict(family="IBM Plex Sans, sans-serif", color=HUD_INK, size=13)


def _mix_value(mix: pd.DataFrame, world: str, col: str) -> int:
    hit = mix.loc[mix["world"] == world, col]
    return int(hit.iloc[0]) if not hit.empty else 0


def open_by_world_figure(mix: pd.DataFrame) -> go.Figure:
    labels = [WORLD_LABEL[world] for world in WORLD_ORDER]
    colors = [WORLD_COLORS[world] for world in WORLD_ORDER]
    fig = go.Figure(
        go.Bar(
            x=[_mix_value(mix, world, "open_n") for world in WORLD_ORDER],
            y=labels,
            orientation="h",
            marker=dict(color=colors, line=dict(width=0)),
            hovertemplate="%{y}: %{x}<extra></extra>",
        )
    )
    fig.update_layout(
        title="Открытые карточки",
        margin=dict(l=8, r=8, t=40, b=8),
        height=200,
        paper_bgcolor=HUD_SCENE,
        plot_bgcolor=HUD_SCENE,
        font=_FONT,
        xaxis=dict(title="штук", dtick=1, gridcolor=HUD_RULE, color=HUD_INK),
        yaxis=dict(title="", color=HUD_INK),
        showlegend=False,
    )
    return fig


def open_by_status_figure(mix: pd.DataFrame) -> go.Figure:
    labels = [WORLD_LABEL[world] for world in WORLD_ORDER]
    series = (
        ("now_n", "now"),
        ("queued_n", "queued"),
        ("paused_n", "paused"),
    )
    fig = go.Figure()
    for col, status in series:
        fig.add_trace(
            go.Bar(
                name=STATUS_LABEL[status],
                x=labels,
                y=[_mix_value(mix, world, col) for world in WORLD_ORDER],
                marker=dict(color=STATUS_COLORS[status], line=dict(width=0)),
                hovertemplate="%{x} · " + STATUS_LABEL[status] + ": %{y}<extra></extra>",
            )
        )
    fig.update_layout(
        title="Открытые по статусу",
        barmode="stack",
        margin=dict(l=8, r=8, t=40, b=32),
        height=240,
        paper_bgcolor=HUD_SCENE,
        plot_bgcolor=HUD_SCENE,
        font=_FONT,
        yaxis=dict(title="штук", dtick=1, gridcolor=HUD_RULE, color=HUD_INK),
        xaxis=dict(title="", color=HUD_INK),
        legend=dict(
            orientation="h",
            y=-0.22,
            x=0,
            font=dict(color=HUD_INK),
            bgcolor="rgba(0,0,0,0)",
        ),
        colorway=list(STATUS_COLORS.values()),
    )
    return fig
