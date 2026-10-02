"""How big the broker pay pool is and which lines of coverage drive its growth."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from figures.analyses.common import Chart, line_name, moved, nice_step, unit
from figures.data import Filters, Tables, subset
from figures.theme import (
    ACCENT,
    BLACK,
    GREY,
    GRID,
    KEEP_STYLE,
    PALETTE,
    RED,
    USD,
    base_theme,
    empty_figure,
    fade,
    growth,
    join_names,
    money,
)

# 1. Is the broker compensation pool growing faster than the lives it covers?


def market_by_year(
    t: Tables, f: Filters, lines: list[str] | None = None
) -> pd.DataFrame:
    df = subset(t.contracts, f)
    if lines:
        df = df[df["line"].isin(lines)]
    market = (
        df.groupby("year")[
            [
                "commissions",
                "fees",
                "lives",
                "tr_premium",
                "tr_compensation",
                "contracts",
                "partial_contracts",
            ]
        ]
        .sum()
        .reindex(f.years, fill_value=0)
    )
    market["compensation"] = market["commissions"] + market["fees"]
    market["comp_per_life"] = market["compensation"] / market["lives"].replace(
        0, np.nan
    )
    market["take_rate"] = (
        market["tr_compensation"] / market["tr_premium"].replace(0, np.nan) * 100
    )
    market["fee_share"] = (
        market["fees"] / market["compensation"].replace(0, np.nan) * 100
    )
    return market


def pay_pool(
    t: Tables, f: Filters, lines: list[str] | None = None, height: int = 430
) -> Chart:
    market = market_by_year(t, f, lines)
    first, last = market.iloc[0], market.iloc[-1]
    if first["compensation"] <= 0 or last["compensation"] <= 0:
        return Chart(
            "Not enough filings for this selection",
            "",
            empty_figure("No broker pay reported", height),
        )

    comp_growth = growth(last["compensation"], first["compensation"])
    lives_growth = growth(last["lives"], first["lives"])
    if comp_growth > lives_growth:
        headline = f"Broker pay {moved(comp_growth)} while covered lives {moved(lives_growth, only=True)}"
    else:
        headline = f"Covered lives {moved(lives_growth)} while broker pay {moved(comp_growth, only=True)}"
    caption = (
        f"Commissions and carrier-paid fees on welfare-plan insurance contracts (Schedule A), "
        f"{f.start} to {f.end}. The line is pay per covered life, which moved from "
        f"\\${first['comp_per_life']:.2f} to \\${last['comp_per_life']:.2f}."
    )
    if last["partial_contracts"] > 0:
        share = last["partial_contracts"] / last["contracts"] * 100
        caption += (
            f" {share:.0f}% of {f.end} contracts cover a policy year under 12 months and "
            "are counted as reported, not annualized."
        )

    scale, suffix = unit(market["compensation"].max())
    x = [str(y) for y in market.index]
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=x,
            y=market["commissions"] / scale,
            name="Commissions",
            marker_color=PALETTE[2],
            customdata=market["contracts"],
            hovertemplate=f"%{{x}}<br>Commissions {USD}%{{y:.2f}}{suffix}"
            "<br>%{customdata:,.0f} contracts<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            x=x,
            y=market["fees"] / scale,
            name="Carrier-paid fees",
            marker_color=PALETTE[0],
            text=[money(v) for v in market["compensation"]],
            textposition="outside",
            textfont=dict(size=13, color=BLACK),
            cliponaxis=False,
            hovertemplate=f"%{{x}}<br>Fees {USD}%{{y:.2f}}{suffix}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x,
            y=market["comp_per_life"],
            name="Pay per covered life",
            yaxis="y2",
            mode="lines+markers+text",
            line=dict(color=ACCENT, width=3),
            marker=dict(size=10, color=ACCENT, line=dict(color="white", width=2)),
            text=[f"{USD}{v:.2f}" for v in market["comp_per_life"]],
            textposition="top center",
            textfont=dict(color=ACCENT, size=12),
            cliponaxis=False,
            hovertemplate=f"%{{x}}<br>{USD}%{{y:.2f}} per covered life<extra></extra>",
        )
    )
    base_theme(fig, height, margin=dict(l=10, r=10, t=30, b=10))

    top = market["compensation"].max() / scale * 1.6
    step = nice_step(top / 1.6)
    ticks = np.arange(0, top, step)
    lo, hi = market["comp_per_life"].min(), market["comp_per_life"].max()
    span = max(hi - lo, hi * 0.02) / 0.24
    fig.update_layout(
        barmode="stack",
        bargap=0.35,
        legend=dict(traceorder="normal", y=1.0, yanchor="bottom"),
        yaxis=dict(
            range=[0, top],
            tickvals=ticks,
            ticktext=[f"{USD}{v:g}{suffix}" for v in ticks],
            gridcolor=GRID,
            zeroline=False,
        ),
        yaxis2=dict(
            overlaying="y",
            side="right",
            range=[lo - 0.68 * span, lo + 0.32 * span],
            showgrid=False,
            showticklabels=False,
            zeroline=False,
        ),
        xaxis=dict(type="category"),
    )
    return Chart(headline, caption, fig)


# 2. Which lines of coverage are driving the growth in broker compensation?

BRIDGE_LABELS = {
    "Multi-line bundle": "Multi-line<br>bundle",
    "Voluntary & other": "Voluntary<br>& other",
    "Life & AD&D": "Life &<br>AD&D",
    "Unclassified": "Not<br>classified",
}


def growth_bridge(
    t: Tables, f: Filters, focus: list[str] | None = None, height: int = 400
) -> Chart:
    shapes: list[dict] = []
    df = subset(t.contracts, f)
    df = df[df["year"].isin([f.start, f.end])].assign(
        comp=lambda d: d["commissions"] + d["fees"]
    )
    by_line = (
        df.pivot_table(index="line", columns="year", values="comp", aggfunc="sum")
        .reindex(columns=[f.start, f.end])
        .fillna(0)
    )
    if by_line.empty or by_line[f.start].sum() <= 0:
        return Chart(
            "Not enough filings for this selection",
            "",
            empty_figure("No broker pay reported", height),
        )

    by_line["change"] = by_line[f.end] - by_line[f.start]
    by_line["pct"] = [growth(n, o) for n, o in zip(by_line[f.end], by_line[f.start])]
    main = by_line.drop("Unclassified", errors="ignore").sort_values(
        "change", ascending=False
    )
    by_line = pd.concat(
        [main, by_line.loc[by_line.index.intersection(["Unclassified"])]]
    )

    total_first, total_last = by_line[f.start].sum(), by_line[f.end].sum()
    net = total_last - total_first
    if net > 0:
        top_two = main.head(2)
        share = top_two["change"].sum() / net * 100
        names = [line_name(n) for n in top_two.index]
        names[0] = names[0][0].upper() + names[0][1:]
        headline = f"{join_names(names)} drove {share:.0f}% of the {money(net, plotly=False)} increase in broker pay"
    else:
        worst = main.sort_values("change").index[0]
        headline = (
            f"Broker pay fell {money(-net, plotly=False)}, led by {line_name(worst)}"
        )
    caption = f"Change in broker pay (commissions and carrier-paid fees) by line of coverage, {f.start} to {f.end}. Click a line to filter the page."

    # Build the bridge from bars so each step can be clicked and dimmed individually
    labels, bases, heights, colors, texts, custom = [], [], [], [], [], []
    labels.append(f"{f.start}<br>total")
    bases.append(0), heights.append(total_first), colors.append(PALETTE[2])
    texts.append(money(total_first, 2)), custom.append("")
    running = total_first
    for line, row in by_line.iterrows():
        c = row["change"]
        labels.append(BRIDGE_LABELS.get(line, line))
        bases.append(running if c >= 0 else running + c)
        heights.append(abs(c))
        colors.append(PALETTE[0] if c >= 0 else RED)
        pct = f"({row['pct']:+.0f}%)" if np.isfinite(row["pct"]) else "(new)"
        texts.append(
            f"{'+' if c >= 0 else '-'}{money(abs(c), 1 if abs(c) >= 1e9 else 0)}<br>{pct}"
        )
        custom.append(line)
        running += c
    labels.append(f"{f.end}<br>total")
    bases.append(0), heights.append(total_last), colors.append(PALETTE[2])
    texts.append(money(total_last, 2)), custom.append("")

    if focus:
        colors = [
            c if (line in focus or line == "") else fade(c, 0.7)
            for c, line in zip(colors, custom)
        ]

    scale, suffix = unit(max(total_first, total_last))
    fig = go.Figure(
        go.Bar(
            x=labels,
            y=np.array(heights) / scale,
            base=np.array(bases) / scale,
            marker=dict(color=colors),
            text=texts,
            textposition="outside",
            textfont=dict(size=11, color=BLACK),
            cliponaxis=False,
            customdata=custom,
            hovertemplate="%{x}<extra></extra>",
            showlegend=False,
            **KEEP_STYLE,
        )
    )
    # Dotted connectors between steps
    levels = np.cumsum([total_first] + list(by_line["change"])) / scale
    for i, level in enumerate(levels):
        shapes.append(
            dict(
                type="line",
                x0=i + 0.3,
                x1=i + 0.7,
                y0=level,
                y1=level,
                line=dict(color=GREY, width=1, dash="dot"),
                xref="x",
                yref="y",
            )
        )
    base_theme(fig, height, margin=dict(l=10, r=10, t=30, b=10))
    lo = min(total_first, total_last, levels.min() * scale) * 0.6 / scale
    hi = max(levels.max(), total_last / scale) * 1.1
    step = nice_step(hi - lo)
    ticks = np.arange(np.floor(lo / step) * step, hi, step)
    fig.update_layout(
        bargap=0.25,
        yaxis=dict(
            range=[lo, hi],
            tickvals=ticks,
            ticktext=[f"{USD}{v:g}{suffix}" for v in ticks],
            gridcolor=GRID,
            zeroline=False,
        ),
        xaxis=dict(tickangle=0, tickfont=dict(size=11)),
    )
    fig.update_layout(shapes=shapes)
    return Chart(headline, caption, fig)
