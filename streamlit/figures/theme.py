"""Chart styling, adapted from the notebook's base_theme and the project style module."""

from itertools import pairwise
from typing import Literal

import numpy as np
import plotly.graph_objects as go

# Palette (same values as the notebook's style module)
PALETTE = ["#86BC25", "#43B02A", "#046A38"]
ACCENT = "#0D8390"
ACCENT_2 = "#007CB0"
BLACK = "#000000"
GREY = "#929292"
RED = "#AA3036"

# Named colors st.badge accepts
BadgeColor = Literal[
    "red", "orange", "yellow", "blue", "green", "violet", "gray", "grey", "primary"
]

# Neutrals for gridlines and muted marks
GRID = "#EDEDED"
MUTED = "#D5D5D5"
FAINT = "#F4F4F4"
GREEN_SCALE = [[0, "#F2F8E6"], [0.5, PALETTE[0]], [1, PALETTE[2]]]

FONT = "Public Sans, Arial, sans-serif"
USD = "&#36;"  # HTML-escaped $ so Plotly never treats $...$ as LaTeX

# Stops Plotly from fading unclicked points since the page does its own highlighting. Not using
# per-bar opacity either since it breaks clicks on bars with text labels
KEEP_STYLE = dict(
    selected=dict(marker=dict(opacity=1)), unselected=dict(marker=dict(opacity=1))
)

# No hover toolbar or scroll zoom
PLOTLY_CONFIG = {"displayModeBar": False, "scrollZoom": False, "responsive": True}


def base_theme(fig: go.Figure, height: int, margin: dict | None = None) -> go.Figure:
    """Base styling for every chart. No titles since the page shows the headline."""
    fig.update_layout(
        template="plotly_white",
        colorway=PALETTE,
        height=height,
        margin=margin or dict(l=10, r=10, t=10, b=10),
        font=dict(family=FONT, color=BLACK, size=12),
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="right",
            x=1,
            font=dict(color=BLACK),
            bgcolor="rgba(0,0,0,0)",
        ),
        hoverlabel=dict(
            bgcolor="white",
            bordercolor=MUTED,
            font=dict(family=FONT, color=BLACK, size=12),
        ),
        xaxis=dict(title_font=dict(color=BLACK), tickfont=dict(color=BLACK)),
        yaxis=dict(title_font=dict(color=BLACK), tickfont=dict(color=BLACK)),
        dragmode=False,
        clickmode="event+select",
    )
    fig.update_traces(marker_line_width=0, selector=dict(type="bar"))
    fig.update_traces(line=dict(width=2), selector=dict(type="scatter"))
    return fig


def fade(color: str, amount: float = 0.6) -> str:
    """Mix a hex color toward white: 0 leaves it unchanged, 1 turns it white."""
    c = color.lstrip("#")
    rgb = [int(c[i : i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{round(v + (255 - v) * amount):02X}" for v in rgb)


def scale_color(value: float, lo: float, hi: float, scale: list = GREEN_SCALE) -> str:
    """Hex color for `value` on a Plotly-style [[position, hex], ...] scale."""
    t = 0.0 if hi <= lo else min(max((value - lo) / (hi - lo), 0.0), 1.0)
    for (p0, c0), (p1, c1) in pairwise(scale):
        if t <= p1:
            w = 0.0 if p1 == p0 else (t - p0) / (p1 - p0)
            a = [int(c0.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4)]
            b = [int(c1.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4)]
            return "#" + "".join(f"{round(x + (y - x) * w):02X}" for x, y in zip(a, b))
    return scale[-1][1]


def empty_figure(message: str, height: int) -> go.Figure:
    """Placeholder shown when a filter leaves too little data to chart."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=13, color=GREY),
    )
    base_theme(fig, height)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def money(v: float, decimals: int = 1, *, plotly: bool = True) -> str:
    """Money like $7.5B. Plotly needs the escaped $ and Streamlit markdown needs a backslash."""
    dollar = USD if plotly else "\\$"
    sign = "-" if v < 0 else ""
    v = abs(float(v))
    for size, suffix in [(1e9, "B"), (1e6, "M"), (1e3, "K")]:
        if v >= size:
            return f"{sign}{dollar}{v / size:.{decimals}f}{suffix}"
    return f"{sign}{dollar}{v:,.0f}"


def count(v: float, decimals: int = 1) -> str:
    """284.2M style for people and plan counts."""
    v = float(v)
    for size, suffix in [(1e9, "B"), (1e6, "M"), (1e3, "K")]:
        if abs(v) >= size:
            return f"{v / size:.{decimals}f}{suffix}"
    return f"{v:,.0f}"


def growth(new, old):
    """Percent change; NaN when the starting value is zero. Works on numbers or Series."""
    if np.isscalar(old):
        return (new / old - 1) * 100 if old else float("nan")
    return (new / old.where(old != 0) - 1) * 100


def join_names(names: list[str]) -> str:
    """'a', 'a and b', 'a, b and c'."""
    names = list(names)
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]


def trend_color(value: float, threshold: float = 0) -> str:
    """Green for up, red for down, grey for flat (within the threshold)."""
    if value > threshold:
        return PALETTE[2]
    if value < -threshold:
        return RED
    return GREY
