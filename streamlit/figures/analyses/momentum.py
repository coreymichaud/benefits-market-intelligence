"""The broker momentum map and the quadrant badge the Brokers page shows for a firm."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from figures.analyses.common import Chart, fit
from figures.analyses.firms import firm_stats, leaderboard_firms
from figures.data import Filters, Tables
from figures.theme import (
    BLACK,
    GREY,
    GRID,
    KEEP_STYLE,
    PALETTE,
    base_theme,
    empty_figure,
    join_names,
)

QUADRANTS = {
    (True, True): ("Growing, keeping clients", "green", ":material/trending_up:"),
    (True, False): ("Growing, losing clients", "blue", ":material/swap_vert:"),
    (False, True): ("Shrinking, keeping clients", "gray", ":material/trending_flat:"),
    (False, False): ("Shrinking, losing clients", "red", ":material/trending_down:"),
}


def momentum_status(stats: pd.DataFrame, firm: str) -> tuple[str, str, str] | None:
    """Which momentum-map quadrant a firm sits in: (label, badge color, icon)."""
    if stats.empty or firm not in stats.index:  # no national firm serves this slice
        return None
    mapped = _momentum_firms(stats)
    peers = mapped["retention"].dropna()
    if firm not in mapped.index or peers.empty:
        return None
    row = stats.loc[firm]
    if not (np.isfinite(row["retention"]) and row["plans_first"] > 0):
        return None
    return QUADRANTS[
        (row["plans_last"] > row["plans_first"], row["retention"] >= peers.median())
    ]


def _momentum_firms(stats: pd.DataFrame) -> pd.DataFrame:
    """Leaderboard firms with enough history to place on the momentum map."""
    if (
        stats.empty
    ):  # firm_stats returns a frame with no columns when no firm serves the slice
        return stats
    firms = leaderboard_firms(stats)
    return firms[(firms["plans_first"] >= 3) & (firms["kept"] + firms["lost"] >= 5)]


def _label_positions(
    x: np.ndarray,
    y: np.ndarray,
    labels: list[str],
    size: np.ndarray,
    x_range: tuple[float, float],
    y_range: tuple[float, float],
    width: float,
    height: float,
    reserved: tuple = (),
) -> list[str]:
    """Pick a text position for each bubble label that avoids other labels and bubbles.

    `reserved` holds (x, y, w, h) pixel boxes that labels should also avoid.
    """
    px = (x - x_range[0]) / (x_range[1] - x_range[0]) * width
    py = (y - y_range[0]) / (y_range[1] - y_range[0]) * height
    pad = 4  # breathing room around each label, in pixels
    options = {
        "top center": lambda i, w: (px[i] - w / 2, py[i] + size[i] / 2 + 1, w, 14),
        "bottom center": lambda i, w: (px[i] - w / 2, py[i] - size[i] / 2 - 15, w, 14),
        "middle right": lambda i, w: (px[i] + size[i] / 2 + 3, py[i] - 7, w, 14),
        "middle left": lambda i, w: (px[i] - size[i] / 2 - 3 - w, py[i] - 7, w, 14),
        "top right": lambda i, w: (px[i] + size[i] * 0.3, py[i] + size[i] * 0.3, w, 14),
        "top left": lambda i, w: (
            px[i] - size[i] * 0.3 - w,
            py[i] + size[i] * 0.3,
            w,
            14,
        ),
        "bottom right": lambda i, w: (
            px[i] + size[i] * 0.3,
            py[i] - size[i] * 0.3 - 14,
            w,
            14,
        ),
        "bottom left": lambda i, w: (
            px[i] - size[i] * 0.3 - w,
            py[i] - size[i] * 0.3 - 14,
            w,
            14,
        ),
    }
    placed, chosen = list(reserved), []
    bubbles = [
        (px[i] - size[i] * 0.4, py[i] - size[i] * 0.4, size[i] * 0.8, size[i] * 0.8)
        for i in range(len(x))
    ]

    def overlap(a, b):
        dx = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
        dy = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
        return max(dx, 0) * max(dy, 0)

    for i in np.argsort(-size):  # big bubbles pick first
        w = len(labels[i]) * 6.4
        best, best_cost = "top center", float("inf")
        for rank, (pos, box) in enumerate(options.items()):
            x0, y0, bw, bh = box(i, w)
            b = (x0 - pad, y0 - pad / 2, bw + 2 * pad, bh + pad)
            cost = (
                2 * sum(overlap(b, o) for o in placed)
                + sum(overlap(b, bub) for j, bub in enumerate(bubbles) if j != i)
                + rank * 0.5
            )  # prefer the plainer positions when costs tie
            spill = (
                max(0, -b[0])
                + max(0, b[0] + b[2] - width)
                + max(0, -b[1])
                + max(0, b[1] + b[3] - height)
            )
            cost += spill * 40
            if cost < best_cost - 1e-6:
                best, best_cost = pos, cost
        x0, y0, bw, bh = options[best](i, w)
        placed.append((x0 - pad, y0 - pad / 2, bw + 2 * pad, bh + pad))
        chosen.append((i, best))
    return [pos for _, pos in sorted(chosen)]


def _corner_boxes(width: float, height: float, w: float = 160, h: float = 16) -> tuple:
    """Pixel boxes of the four quadrant captions in the momentum map's corners."""
    return (
        (0, height - h, w, h),
        (width - w, height - h, w, h),
        (0, 0, w, h),
        (width - w, 0, w, h),
    )


def momentum_map(
    t: Tables, f: Filters, focus: str | None = None, height: int = 460
) -> Chart:
    """Combines analyses 5 and 9: growth in plans served against client retention."""
    notes: list[dict] = []
    shapes: list[dict] = []
    stats = firm_stats(t, f)
    firms = _momentum_firms(stats)
    if len(firms) < 3:
        return Chart(
            "Too few broker relationships for this selection",
            "",
            empty_figure("Too few plans", height),
        )

    firms = firms.copy()
    firms["ratio"] = np.log2(firms["plans_last"].clip(lower=0.5) / firms["plans_first"])
    median_ret = firms["retention"].median()
    ahead = firms[
        (firms["ratio"] > 0) & (firms["retention"] >= median_ret)
    ].sort_values("growth", ascending=False)
    behind = firms[
        (firms["ratio"] < 0) & (firms["retention"] < median_ret)
    ].sort_values("growth")
    lead = ahead.index[:2].tolist()
    lag = behind.index[:1].tolist()
    if lead:
        headline = f"{join_names(lead)} {'is' if len(lead) == 1 else 'are'} growing and keeping clients"
        if lag:
            headline = fit(
                headline + f"; {lag[0]} is losing ground", headline, limit=112
            )
    elif lag:
        headline = f"{lag[0]} is shrinking and losing clients"
    else:
        headline = (
            "No leading firm is both growing and keeping clients above the median"
        )
    caption = (
        f"Change in plans served since {f.start} vs. share of clients kept each year; bubble size is "
        f"plans served in {f.end}. Click a firm to focus it."
    )

    x_lo, x_hi = (
        min(firms["ratio"].min(), -0.3) - 0.3,
        max(firms["ratio"].max(), 0.3) + 0.35,
    )
    y_lo, y_hi = (
        firms["retention"].min() - 2.5,
        min(firms["retention"].max() + 2.5, 101),
    )
    fig = go.Figure()
    shapes.append(
        dict(
            type="rect",
            x0=0,
            x1=x_hi,
            y0=median_ret,
            y1=y_hi,
            fillcolor="rgba(134, 188, 37, 0.10)",
            line_width=0,
            layer="below",
        )
    )
    shapes.append(
        dict(
            type="line",
            xref="x",
            yref="paper",
            x0=0,
            x1=0,
            y0=0,
            y1=1,
            line=dict(color=GREY, width=1, dash="dot"),
        )
    )
    shapes.append(
        dict(
            type="line",
            xref="paper",
            yref="y",
            x0=0,
            x1=1,
            y0=median_ret,
            y1=median_ret,
            line=dict(color=GREY, width=1, dash="dot"),
        )
    )
    for x, y, xa, ya, text in [
        (x_hi, y_hi, "right", "top", "Growing, keeping clients"),
        (x_lo, y_hi, "left", "top", "Shrinking, keeping clients"),
        (x_hi, y_lo, "right", "bottom", "Growing, losing clients"),
        (x_lo, y_lo, "left", "bottom", "Shrinking, losing clients"),
    ]:
        notes.append(
            dict(
                x=x,
                y=y,
                xanchor=xa,
                yanchor=ya,
                text=text,
                showarrow=False,
                font=dict(size=11, color=GREY),
            )
        )
    size = (
        np.sqrt(firms["plans_last"]) / np.sqrt(firms["plans_last"].max()) * 32 + 10
    ).to_numpy()
    colors = [
        PALETTE[2]
        if firm == focus
        else PALETTE[0]
        if (r > 0 and ret >= median_ret)
        else "#BDBDBD"
        for firm, r, ret in zip(firms.index, firms["ratio"], firms["retention"])
    ]
    positions = _label_positions(
        firms["ratio"].to_numpy(),
        firms["retention"].to_numpy(),
        list(firms.index),
        size,
        (x_lo, x_hi),
        (y_lo, y_hi),
        width=720,
        height=height - 60,
        reserved=_corner_boxes(720, height - 60),
    )
    fig.add_trace(
        go.Scatter(
            x=firms["ratio"],
            y=firms["retention"],
            mode="markers+text",
            marker=dict(
                size=size,
                color=colors,
                opacity=0.92,
                line=dict(color="white", width=1.5),
            ),
            text=[f"<b>{firm}</b>" if firm == focus else firm for firm in firms.index],
            textposition=positions,
            textfont=dict(size=11, color=BLACK),
            customdata=np.column_stack(
                [firms.index, firms["growth"], firms["plans_last"]]
            ),
            hovertemplate="<b>%{customdata[0]}</b><br>Plans served: %{customdata[1]:+.0f}% "
            f"(%{{customdata[2]:.0f}} in {f.end})<br>Clients kept: %{{y:.0f}}%<extra></extra>",
            cliponaxis=False,
            showlegend=False,
            **KEEP_STYLE,
        )
    )
    tick_ratios = [r for r in [-2, -1, -0.415, 0, 0.585, 1, 2, 3] if x_lo <= r <= x_hi]
    base_theme(fig, height, margin=dict(l=10, r=10, t=10, b=10))
    fig.update_layout(
        xaxis=dict(
            title=f"Change in plans served, {f.start}-{f.end}",
            range=[x_lo, x_hi],
            tickvals=tick_ratios,
            ticktext=[f"{(2**r - 1) * 100:+.0f}%" for r in tick_ratios],
            gridcolor=GRID,
            zeroline=False,
            title_font=dict(size=11, color=GREY),
            tickfont=dict(size=11),
        ),
        yaxis=dict(
            title="Clients kept year to year",
            range=[y_lo, y_hi],
            ticksuffix="%",
            gridcolor=GRID,
            zeroline=False,
            title_font=dict(size=11, color=GREY),
            tickfont=dict(size=11),
        ),
    )
    fig.update_layout(annotations=notes, shapes=shapes)
    return Chart(headline, caption, fig)
