"""Dashboard versions of the analyses in notebooks/analysis.ipynb.

Each builder returns a Chart whose headline is recomputed for the active filters.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from figures.data import (
    SELF_FUNDING_BANDS,
    STATE_NAMES,
    VOLUNTARY_BANDS,
    Filters,
    Tables,
    subset,
)
from figures.theme import (
    ACCENT,
    KEEP_STYLE,
    BLACK,
    FAINT,
    GREEN_SCALE,
    GREY,
    GRID,
    MUTED,
    PALETTE,
    RED,
    USD,
    base_theme,
    empty_figure,
    fade,
    growth,
    join_names,
    money,
    scale_color,
    trend_color,
)


@dataclass
class Chart:
    headline: str
    caption: str
    figure: go.Figure


# Friendlier names when a line of coverage sits mid-sentence
LINE_NAMES = {
    "Multi-line bundle": "multi-line bundles",
    "Voluntary & other": "voluntary benefits",
    "Life & AD&D": "life & AD&D",
    "Stop-loss": "stop-loss",
}
GLOBAL_CONSULTANCIES = {"WTW", "Mercer", "Aon"}


def _line_name(line: str) -> str:
    return LINE_NAMES.get(line, line.lower())


def _moved(pct: float, only: bool = False) -> str:
    """'grew 41%', 'grew only 17%', 'fell 5%', 'held flat' for headlines."""
    if abs(pct) < 0.5:
        return "held flat"
    if pct > 0:
        return f"grew {'only ' if only else ''}{pct:.0f}%"
    return f"fell {abs(pct):.0f}%"


def _fit(*candidates: str, limit: int) -> str:
    """First headline that fits on one line of its panel (candidates go from richest to shortest)."""
    for text in candidates:
        if len(text) <= limit:
            return text
    return candidates[-1]


def _nice_step(span: float, target_ticks: int = 4) -> float:
    raw = span / target_ticks
    magnitude = 10 ** np.floor(np.log10(raw))
    for m in [1, 2, 2.5, 5, 10]:
        if m * magnitude >= raw:
            return m * magnitude
    return 10 * magnitude


def _unit(value: float) -> tuple[float, str]:
    return (1e9, "B") if value >= 1e9 else (1e6, "M") if value >= 1e6 else (1e3, "K")


# 1. Is the broker compensation pool growing faster than the lives it covers?


def market_by_year(
    t: Tables, f: Filters, lines: list[str] | None = None
) -> pd.DataFrame:
    df = subset(t.contracts, f)
    if lines:
        df = df[df["line"].isin(lines)]
    market = (
        df.groupby("year")[
            ["commissions", "fees", "lives", "tr_premium", "tr_compensation"]
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
        headline = f"Broker pay {_moved(comp_growth)} while covered lives {_moved(lives_growth, only=True)}"
    else:
        headline = f"Covered lives {_moved(lives_growth)} while broker pay {_moved(comp_growth, only=True)}"
    caption = (
        f"Commissions and carrier-paid fees on welfare-plan insurance contracts (Schedule A), "
        f"{f.start}–{f.end}. The line is pay per covered life, which moved from "
        f"\\${first['comp_per_life']:.2f} to \\${last['comp_per_life']:.2f}."
    )

    scale, suffix = _unit(market["compensation"].max())
    x = [str(y) for y in market.index]
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=x,
            y=market["commissions"] / scale,
            name="Commissions",
            marker_color=PALETTE[2],
            hovertemplate=f"%{{x}}<br>Commissions {USD}%{{y:.2f}}{suffix}<extra></extra>",
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
    step = _nice_step(top / 1.6)
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
        names = [_line_name(n) for n in top_two.index]
        names[0] = names[0][0].upper() + names[0][1:]
        headline = f"{join_names(names)} drove {share:.0f}% of the {money(net, plotly=False)} increase in broker pay"
    else:
        worst = main.sort_values("change").index[0]
        headline = (
            f"Broker pay fell {money(-net, plotly=False)}, led by {_line_name(worst)}"
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

    scale, suffix = _unit(max(total_first, total_last))
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
    step = _nice_step(hi - lo)
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


# 3. Is broker pay shifting from commissions toward carrier-paid fees?


def fee_adoption(
    t: Tables, f: Filters, focus: list[str] | None = None, height: int = 400
) -> Chart:
    notes: list[dict] = []
    df = subset(t.contracts, f)
    df = df[df["line"] != "Unclassified"]
    agg = df.groupby(["line", "year"])[["fee_contracts", "contracts"]].sum()
    agg = agg[agg["contracts"] >= 20]
    fee_mix = (agg["fee_contracts"] / agg["contracts"] * 100).unstack("year")
    fee_mix = fee_mix.reindex(columns=f.years).dropna(subset=[f.start, f.end])
    if fee_mix.empty:
        return Chart(
            "Not enough contracts for this selection",
            "",
            empty_figure("Too few contracts", height),
        )

    fee_mix["delta"] = fee_mix[f.end] - fee_mix[f.start]
    fee_mix = fee_mix.sort_values(f.end)
    rising = fee_mix[fee_mix["delta"] >= 2].sort_values("delta", ascending=False)
    if len(rising):
        lead = rising.index[0]
        where = (
            "every line"
            if len(rising) == len(fee_mix)
            else f"{len(rising)} of {len(fee_mix)} lines"
        )
        led = f"led by {_line_name(lead)} (+{rising.loc[lead, 'delta']:.0f} pts)"
        headline = _fit(
            f"Carrier-paid fees are spreading: up 2+ pts in {where} since {f.start}, {led}",
            f"Carrier-paid fees are up 2+ pts in {where}, {led}",
            limit=100,
        )
    else:
        headline = f"Carrier-paid fee adoption has not moved much since {f.start}"
    caption = "Contracts where the carrier paid the broker fees (bonuses, overrides, service fees), not just commissions."

    z = fee_mix[f.years].values
    z_max = np.ceil(np.nanmax(z) / 10) * 10
    rows = [
        f"<b>{line}</b>" if focus and line in focus else line for line in fee_mix.index
    ]
    fig = go.Figure(
        go.Heatmap(
            z=z,
            x=[str(y) for y in f.years],
            y=rows,
            colorscale=GREEN_SCALE,
            zmin=0,
            zmax=z_max,
            xgap=3,
            ygap=3,
            showscale=False,
            text=[[f"{v:.0f}%" if np.isfinite(v) else "" for v in row] for row in z],
            texttemplate="%{text}",
            textfont=dict(size=12),
            hovertemplate="%{y}<br>%{x}: %{z:.1f}% of contracts<extra></extra>",
        )
    )
    for row_label, d in zip(rows, fee_mix["delta"]):
        d_round = round(d)
        text = "flat" if abs(d_round) < 2 else f"{d_round:+d} pts"
        notes.append(
            dict(
                x=1.01,
                xref="paper",
                y=row_label,
                yref="y",
                text=f"<b>{text}</b>",
                showarrow=False,
                xanchor="left",
                font=dict(size=12, color=trend_color(d, 1.5)),
            )
        )
    base_theme(fig, height, margin=dict(l=10, r=70, t=30, b=10))
    fig.update_layout(
        xaxis=dict(type="category", side="top", showgrid=False, tickfont=dict(size=12)),
        yaxis=dict(showgrid=False, tickfont=dict(size=12)),
    )
    fig.update_layout(annotations=notes)
    return Chart(headline, caption, fig)


# 7. What share of premium are brokers capturing, and is that take rate compressing by line?


def take_rate(
    t: Tables, f: Filters, focus: list[str] | None = None, height: int = 400
) -> Chart:
    notes: list[dict] = []
    shapes: list[dict] = []
    df = subset(t.contracts, f)
    df = df[df["line"] != "Unclassified"]
    agg = df.groupby(["line", "year"])[["tr_compensation", "tr_premium"]].sum()
    agg = agg[agg["tr_premium"] > 0]
    rates = (
        (agg["tr_compensation"] / agg["tr_premium"] * 100)
        .unstack("year")
        .reindex(columns=f.years)
    )
    rates = rates.dropna(subset=[f.start, f.end])
    if rates.empty:
        return Chart(
            "Not enough premium data for this selection",
            "",
            empty_figure("Too few contracts", height),
        )

    premium_last = (
        agg["tr_premium"].xs(f.end, level="year").reindex(rates.index).fillna(0)
    )
    rates = rates.loc[premium_last.sort_values(ascending=False).index]
    rate_change = rates.div(rates[f.start], axis=0).sub(1).mul(100)
    overall = df.groupby("year")[["tr_compensation", "tr_premium"]].sum()
    overall_rate = overall["tr_compensation"] / overall["tr_premium"] * 100

    final = rate_change[f.end]
    rising = final[final >= 3].sort_values(ascending=False).index
    falling = final[final <= -3].sort_values().index
    up = join_names([_line_name(n) for n in rising[:2]])
    down = join_names([_line_name(n) for n in falling[:2]])
    if len(falling) and len(rising):
        headline = _fit(
            f"Take rates are compressing in {down} but climbing in {up}",
            f"Take rates are compressing in {_line_name(falling[0])} but climbing in {up}",
            f"Take rates are compressing in {_line_name(falling[0])} but climbing in {_line_name(rising[0])}",
            limit=100,
        )
    elif len(rising):
        headline = f"Take rates are climbing in {up}"
    elif len(falling):
        headline = f"Take rates are compressing in {down}"
    else:
        headline = "Take rates are broadly flat across lines of coverage"
    caption = (
        f"Take rate is broker pay divided by premium (contracts under \\$250M). Market-wide: "
        f"{overall_rate[f.start]:.2f}% in {f.start}, {overall_rate[f.end]:.2f}% in {f.end}."
    )

    n_cols = 4
    n_rows = int(np.ceil(len(rates) / n_cols))
    fig = make_subplots(
        rows=n_rows,
        cols=n_cols,
        shared_yaxes=True,
        horizontal_spacing=0.035,
        vertical_spacing=0.2,
    )
    y_min = (
        np.floor(min(np.nanmin(rate_change.values), -5) / 10) * 10 - 3
    )  # keep the lowest tick off the x labels
    y_max = np.ceil(np.nanmax(rate_change.values) / 10) * 10 + 5
    fills = {PALETTE[2]: "rgba(4, 106, 56, 0.12)", RED: "rgba(170, 48, 54, 0.12)"}
    for i, line in enumerate(rates.index):
        row, col = i // n_cols + 1, i % n_cols + 1
        pct = final[line]
        color = trend_color(pct, 3)
        dim = bool(focus) and line not in focus
        fig.add_trace(
            go.Scatter(
                x=f.years,
                y=rate_change.loc[line],
                mode="lines+markers",
                line=dict(color=MUTED if dim else color, width=2.5),
                fill="tozeroy",
                fillcolor="rgba(0,0,0,0.03)"
                if dim
                else fills.get(color, "rgba(146, 146, 146, 0.12)"),
                marker=dict(
                    size=[0] * (len(f.years) - 1) + [8], color=MUTED if dim else color
                ),
                customdata=rates.loc[line],
                showlegend=False,
                hovertemplate=f"{line}<br>%{{x}}: %{{customdata:.2f}}% take rate "
                f"(%{{y:+.1f}}% vs {f.start})<extra></extra>",
            ),
            row=row,
            col=col,
        )
        axis = "" if i == 0 else str(i + 1)
        shapes.append(
            dict(
                type="line",
                xref=f"x{axis} domain",
                yref=f"y{axis}",
                x0=0,
                x1=1,
                y0=0,
                y1=0,
                line=dict(color=GREY, width=1, dash="dot"),
            )
        )
        notes.append(
            dict(
                x=0,
                y=1.0,
                xref=f"x{axis} domain",
                yref=f"y{axis} domain",
                xanchor="left",
                yanchor="bottom",
                text=f"<b>{line}</b><br>{rates.loc[line, f.start]:.2f}% to {rates.loc[line, f.end]:.2f}%",
                showarrow=False,
                align="left",
                font=dict(size=11, color=GREY if dim else BLACK),
            )
        )
        notes.append(
            dict(
                x=1,
                y=1.0,
                xref=f"x{axis} domain",
                yref=f"y{axis} domain",
                xanchor="right",
                yanchor="bottom",
                text=f"<b>{pct:+.0f}%</b>",
                showarrow=False,
                font=dict(size=13, color=GREY if dim else color),
            )
        )
    fig.update_xaxes(
        tickvals=[f.start, f.end],
        showgrid=False,
        tickfont=dict(size=10, color=GREY),
        range=[f.start - 0.3, f.end + 0.3],
    )
    fig.update_yaxes(
        range=[y_min, y_max],
        ticksuffix="%",
        tickformat="+.0f",
        dtick=10 if y_max - y_min <= 60 else 20,
        gridcolor="#F0F0F0",
        zeroline=False,
        tickfont=dict(size=10, color=GREY),
    )
    base_theme(fig, height, margin=dict(l=10, r=10, t=38, b=10))
    fig.update_layout(annotations=notes, shapes=shapes)
    return Chart(headline, caption, fig)


# 5 & 9. Broker firms: plans served, ranks, wins and losses


def firm_stats(t: Tables, f: Filters) -> pd.DataFrame:
    """One row per firm: plans served and rank by year, plus wins and losses in the range.

    A move between two years is counted in the later year, as in the notebook.
    """
    plans = (
        subset(t.firm_plans, f)
        .groupby(["firm", "year"])["plans"]
        .sum()
        .unstack("year")
        .reindex(columns=f.years)
        .fillna(0)
        .sort_index()
    )
    if plans.empty:
        return pd.DataFrame()
    ranks = plans.rank(ascending=False, method="first").astype(int)

    ev = subset(t.firm_events, f, years=False)
    ev = ev[ev["year"].between(f.start + 1, f.end)]
    kinds = ["won_local", "won_national", "won_other", "lost", "kept"]
    grid = pd.MultiIndex.from_product(
        [plans.index, f.years[1:]], names=["firm", "year"]
    )
    by_year = (
        ev.pivot_table(
            index=["firm", "year"], columns="event", values="plans", aggfunc="sum"
        )
        .reindex(index=grid, columns=kinds)
        .fillna(0)
    )
    totals = by_year.groupby("firm").sum().reindex(plans.index).fillna(0)
    by_year["net"] = by_year["won_local"] + by_year["won_national"] - by_year["lost"]
    by_year["retention"] = (
        by_year["kept"] / (by_year["kept"] + by_year["lost"]).replace(0, np.nan) * 100
    )
    yearly = by_year[["net", "won_local", "retention"]].unstack("year")
    yearly.columns = [f"{a}_{b}" for a, b in yearly.columns]

    out = pd.concat({"plans": plans, "rank": ranks}, axis=1)
    out.columns = [f"{a}_{b}" for a, b in out.columns]
    out = out.join(totals).join(yearly)
    out["plans_first"], out["plans_last"] = plans[f.start], plans[f.end]
    out["rank_first"], out["rank_last"] = ranks[f.start], ranks[f.end]
    out["growth"] = growth(out["plans_last"], out["plans_first"])
    out["won"] = out["won_local"] + out["won_national"]
    out["net"] = out["won"] - out["lost"]
    out["retention"] = (
        out["kept"] / (out["kept"] + out["lost"]).replace(0, np.nan) * 100
    )
    return out.sort_values("rank_last")


def leaderboard_firms(stats: pd.DataFrame) -> pd.DataFrame:
    """Firms in the top 10 at the start or end of the range (the notebook's bump chart set)."""
    return stats[(stats["rank_first"] <= 10) | (stats["rank_last"] <= 10)]


QUADRANTS = {
    (True, True): ("Growing, keeping clients", "green", ":material/trending_up:"),
    (True, False): ("Growing, losing clients", "blue", ":material/swap_vert:"),
    (False, True): ("Shrinking, keeping clients", "gray", ":material/trending_flat:"),
    (False, False): ("Shrinking, losing clients", "red", ":material/trending_down:"),
}


def momentum_status(stats: pd.DataFrame, firm: str) -> tuple[str, str, str] | None:
    """Which momentum-map quadrant a firm sits in: (label, badge color, icon)."""
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


def leaderboard(
    t: Tables, f: Filters, focus: str | None = None, height: int = 520
) -> Chart:
    notes: list[dict] = []
    stats = firm_stats(t, f)
    if stats.empty or (stats["plans_last"] > 0).sum() < 3:
        return Chart(
            "Too few broker relationships for this selection",
            "",
            empty_figure("Too few plans", height),
        )

    shown = stats[(stats["rank_first"] <= 10) | (stats["rank_last"] <= 10)]
    climbers = shown.index[shown["rank_last"] < shown["rank_first"]]
    fallers = shown.index[shown["rank_last"] > shown["rank_first"]]
    top_climbers = (
        shown.loc[climbers].sort_values("growth", ascending=False).index[:3].tolist()
    )
    drop = (
        shown.loc[fallers, "rank_last"] - shown.loc[fallers, "rank_first"]
    ).sort_values(ascending=False)
    if top_climbers:
        global_present = GLOBAL_CONSULTANCIES & set(shown.index)
        if global_present and global_present <= set(fallers):
            tail = " as the global consultancies slip"
        elif len(drop):
            tail = f" while {join_names(drop.index[:2].tolist())} slip"
        else:
            tail = ""

        def say(names: list[str], ending: str) -> str:
            return f"{join_names(names)} {'is' if len(names) == 1 else 'are'} climbing the large-plan leaderboard{ending}"

        headline = _fit(
            say(top_climbers, tail),
            say(top_climbers[:2], tail),
            say(top_climbers[:2], ""),
            limit=125,
        )
    else:
        headline = f"The large-plan leaderboard has barely moved since {f.start}"
    caption = (
        "Rank by single-employer welfare plans naming the firm on Schedule C; circles show plans "
        "served. Click a firm to focus it."
    )

    years = f.years
    fig = go.Figure()
    order = shown.sort_values("rank_last").index.tolist()
    if focus in order:  # draw the focused firm last so it sits on top
        order = [firm for firm in order if firm != focus] + [focus]
    for firm in order:
        row = shown.loc[firm]
        is_focus = firm == focus
        is_climber = firm in climbers
        color = PALETTE[2] if is_focus else PALETTE[0] if is_climber else MUTED
        plans = [row[f"plans_{y}"] for y in years]
        ranks = [row[f"rank_{y}"] if p > 0 else None for y, p in zip(years, plans)]
        fig.add_trace(
            go.Scatter(
                x=years,
                y=ranks,
                mode="lines+markers+text",
                name=firm,
                line=dict(
                    color=color,
                    width=5 if is_focus else 3.5 if is_climber else 2,
                    shape="spline",
                    smoothing=0.6,
                ),
                marker=dict(
                    size=28 if is_focus else 24,
                    color=color,
                    line=dict(color="white", width=2),
                ),
                text=[f"{p:.0f}" for p in plans],
                textfont=dict(
                    color="white" if (is_focus or is_climber) else BLACK, size=10
                ),
                textposition="middle center",
                customdata=[[firm, p] for p in plans],
                hovertemplate=f"<b>{firm}</b><br>%{{x}}: rank %{{y}}, %{{customdata[1]:.0f}} plans<extra></extra>",
                showlegend=False,
                **KEEP_STYLE,
            )
        )
        change = row["growth"]
        label_color = PALETTE[2] if (is_focus or is_climber) else GREY
        font = dict(
            size=12 if is_focus else 11, color=BLACK if is_focus else label_color
        )
        if row["plans_last"] > 0:
            notes.append(
                dict(
                    x=f.end,
                    y=row[f"rank_{f.end}"],
                    xanchor="left",
                    xshift=20,
                    showarrow=False,
                    text=f"<b>{firm}</b>  {change:+.0f}%"
                    if np.isfinite(change)
                    else f"<b>{firm}</b>  new",
                    font=font,
                )
            )
        if row["plans_first"] > 0:
            notes.append(
                dict(
                    x=f.start,
                    y=row[f"rank_{f.start}"],
                    xanchor="right",
                    xshift=-20,
                    showarrow=False,
                    text=firm,
                    font=font,
                )
            )
    base_theme(fig, height, margin=dict(l=150, r=190, t=30, b=10))
    fig.update_layout(
        xaxis=dict(
            tickvals=years,
            showgrid=False,
            side="top",
            range=[f.start - 0.25, f.end + 0.25],
            zeroline=False,
        ),
        yaxis=dict(
            autorange="reversed", showgrid=False, showticklabels=False, zeroline=False
        ),
    )
    fig.update_layout(annotations=notes)
    return Chart(headline, caption, fig)


def win_loss(
    t: Tables, f: Filters, focus: str | None = None, height: int = 460
) -> Chart:
    notes: list[dict] = []
    stats = firm_stats(t, f)
    if stats.empty or f.end == f.start:
        return Chart(
            "Too few broker switches for this selection",
            "",
            empty_figure("Too few switches", height),
        )
    wl = stats.sort_values("rank_last").head(10).sort_values("net")
    if (wl["won"] + wl["lost"]).sum() < 5:
        return Chart(
            "Too few broker switches for this selection",
            "",
            empty_figure("Too few switches", height),
        )

    winners = wl[wl["net"] > 0].sort_values("net", ascending=False).index[:2].tolist()
    losers = wl[wl["net"] < 0].sort_values("net").index[:2].tolist()
    from_local = winners and all(
        wl.loc[w, "won_local"] >= wl.loc[w, "won_national"] for w in winners
    )
    one = len(winners) == 1
    if winners:
        how = (
            "clients from local brokers"
            if from_local
            else "more plans than " + ("it loses" if one else "they lose")
        )
        headline = f"{join_names(winners)} {'wins' if one else 'win'} {how}"
        if losers:
            headline = _fit(
                headline
                + f"; {join_names(losers)} {'loses' if len(losers) == 1 else 'lose'} the most",
                headline + f"; {losers[0]} loses the most",
                headline,
                limit=112,
            )
    elif losers:
        headline = f"{join_names(losers)} {'is' if len(losers) == 1 else 'are'} losing the most plans"
    else:
        headline = "Wins and losses are balanced across the top firms"
    caption = (
        "Plans filing in consecutive years. A win newly names the firm on Schedule C; a loss stops "
        "naming it. Click a firm to focus it."
    )

    def shade(color: str) -> list[str]:
        return [
            color if (not focus or firm == focus) else fade(color, 0.55)
            for firm in wl.index
        ]

    ticks = [f"<b>{firm}</b>" if firm == focus else firm for firm in wl.index]
    fig = go.Figure()
    for col, name, color in [
        ("won_local", "Won from local brokers", PALETTE[2]),
        ("won_national", "Won from national rivals", ACCENT),
    ]:
        fig.add_trace(
            go.Bar(
                y=ticks,
                x=wl[col],
                name=name,
                orientation="h",
                marker=dict(color=shade(color)),
                text=[f"{v:.0f}" if v >= 6 else "" for v in wl[col]],
                textposition="inside",
                insidetextanchor="middle",
                textfont=dict(color="white", size=11),
                customdata=wl.index,
                hovertemplate="%{customdata}<br>" + name + ": %{x}<extra></extra>",
                showlegend=False,
                **KEEP_STYLE,
            )
        )
    fig.add_trace(
        go.Bar(
            y=ticks,
            x=-wl["lost"],
            name="Lost",
            orientation="h",
            marker=dict(color=shade(RED)),
            text=[f"{v:.0f}" if v >= 4 else "" for v in wl["lost"]],
            textposition="inside",
            textfont=dict(color="white", size=11),
            customdata=np.column_stack([wl.index, wl["lost"]]),
            hovertemplate="%{customdata[0]}<br>Lost: %{customdata[1]}<extra></extra>",
            showlegend=False,
            **KEEP_STYLE,
        )
    )
    # Legend-only swatches: the bars' own colors are faded for every firm but the focus
    for name, color in [
        ("Won from local brokers", PALETTE[2]),
        ("Won from national rivals", ACCENT),
        ("Lost", RED),
    ]:
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="markers",
                name=name,
                marker=dict(symbol="square", size=11, color=color),
                hoverinfo="skip",
            )
        )
    x_max = max(wl["won"].max(), 1)
    x_min = max(wl["lost"].max(), 1)
    for label, (_, row) in zip(ticks, wl.iterrows()):
        notes.append(
            dict(
                x=x_max * 1.08,
                y=label,
                text=f"<b>net {row['net']:+.0f}</b>",
                showarrow=False,
                xanchor="left",
                font=dict(size=12, color=trend_color(row["net"])),
            )
        )
    for x, text, anchor in [
        (-x_min * 0.5, "Plans lost", "center"),
        (x_max * 0.5, "Plans won", "center"),
    ]:
        notes.append(
            dict(
                x=x,
                y=-0.06,
                yref="paper",
                yanchor="top",
                text=text,
                showarrow=False,
                xanchor=anchor,
                font=dict(size=11, color=GREY),
            )
        )
    step = _nice_step(x_min + x_max, 6)
    tick_vals = np.arange(-np.ceil(x_min / step) * step, x_max + step, step)
    base_theme(fig, height, margin=dict(l=10, r=10, t=30, b=40))
    fig.update_layout(
        barmode="relative",
        bargap=0.3,
        legend=dict(y=1.0, yanchor="bottom", x=0, xanchor="left", traceorder="normal"),
        xaxis=dict(
            tickvals=tick_vals,
            ticktext=[f"{abs(v):.0f}" for v in tick_vals],
            range=[-x_min * 1.1, x_max * 1.38],
            zeroline=True,
            zerolinecolor=BLACK,
            zerolinewidth=1,
            gridcolor=GRID,
            tickfont=dict(size=11),
        ),
        yaxis=dict(showgrid=False, tickfont=dict(size=12)),
    )
    fig.update_layout(annotations=notes)
    return Chart(headline, caption, fig)


def _momentum_firms(stats: pd.DataFrame) -> pd.DataFrame:
    """Leaderboard firms with enough history to place on the momentum map."""
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
    firms = _momentum_firms(stats) if not stats.empty else stats
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
            headline = _fit(
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
            title=f"Change in plans served, {f.start}–{f.end}",
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


# 10. Where is broker compensation growing fastest?


def state_map(t: Tables, f: Filters, height: int = 400) -> Chart:
    df = subset(t.contracts, f, state=False)
    df = df[df["state"].isin(STATE_NAMES) & df["year"].isin([f.start, f.end])]
    by_state = (
        df.assign(comp=df["commissions"] + df["fees"])
        .pivot_table(index="state", columns="year", values="comp", aggfunc="sum")
        .reindex(columns=[f.start, f.end])
        .dropna()
    )
    by_state = by_state[(by_state[f.start] > 0) & (by_state[f.end] > 0)]
    if len(by_state) < 5:
        return Chart(
            "Too few states with broker pay for this selection",
            "",
            empty_figure("Too few states", height),
        )

    by_state["growth"] = growth(by_state[f.end], by_state[f.start])
    national = growth(by_state[f.end].sum(), by_state[f.start].sum())
    # Same cut-offs as the notebook ($25M / $50M on the full market), scaled to the current slice
    small = by_state[f.end] < by_state[f.end].sum() * 0.0033
    established = by_state[by_state[f.start] >= by_state[f.start].sum() * 0.0093]
    fastest = established["growth"].sort_values(ascending=False).index[:3].tolist()
    largest = by_state[f.end].idxmax()
    lg = by_state.loc[largest, "growth"]
    headline = (
        f"Broker pay is growing fastest in {join_names([STATE_NAMES[s] for s in fastest])}; "
        f"{STATE_NAMES[largest]}, the largest market, {'lags' if lg < national else 'leads'} at {lg:+.0f}%"
    )
    cutoff = money(by_state[f.end].sum() * 0.0033, 0, plotly=False)
    caption = (
        f"Broker pay growth by plan sponsor state, {f.start}–{f.end}, against the U.S. rate of "
        f"{national:+.0f}%. Grey: markets under {cutoff}. Click a state to filter."
    )

    span = max(abs(national), 10)
    fig = go.Figure()
    small_states = by_state.index[small]
    if len(small_states):
        fig.add_trace(
            go.Choropleth(
                locations=small_states,
                locationmode="USA-states",
                z=[0] * len(small_states),
                colorscale=[[0, "#E3E3E3"], [1, "#E3E3E3"]],
                showscale=False,
                marker_line_color="white",
                marker_line_width=1,
                customdata=np.column_stack(
                    [
                        [STATE_NAMES[s] for s in small_states],
                        [money(v) for v in by_state.loc[small, f.end]],
                    ]
                ),
                hovertemplate="<b>%{customdata[0]}</b><br>"
                + str(f.end)
                + " pool: %{customdata[1]} (small market)<extra></extra>",
                unselected=dict(marker=dict(opacity=1)),
            )
        )
    big = by_state[~small]
    fig.add_trace(
        go.Choropleth(
            locations=big.index,
            locationmode="USA-states",
            z=big["growth"],
            zmin=national - span,
            zmax=national + span,
            zmid=national,
            colorscale=[
                [0, RED],
                [0.3, "#E6B3B5"],
                [0.5, FAINT],
                [0.7, PALETTE[0]],
                [1, PALETTE[2]],
            ],
            marker_line_color="white",
            marker_line_width=1,
            customdata=np.column_stack(
                [
                    [STATE_NAMES[s] for s in big.index],
                    [money(v) for v in big[f.start]],
                    [money(v) for v in big[f.end]],
                ]
            ),
            hovertemplate="<b>%{customdata[0]}</b><br>"
            + str(f.start)
            + ": %{customdata[1]}<br>"
            + str(f.end)
            + ": %{customdata[2]}<br>Growth: %{z:+.1f}%<extra></extra>",
            colorbar=dict(
                title=dict(
                    text=f"Growth<br>{f.start}–{f.end}", side="top", font=dict(size=11)
                ),
                tickvals=[national - span, national, national + span],
                ticktext=[
                    f"{national - span:+.0f}% or less",
                    f"U.S. {national:+.0f}%",
                    f"{national + span:+.0f}% or more",
                ],
                thickness=12,
                len=0.7,
                x=0.9,
                tickfont=dict(size=10),
            ),
            unselected=dict(marker=dict(opacity=1)),
        )
    )
    labeled = big[f.end].sort_values(ascending=False).index[:15]
    fig.add_trace(
        go.Scattergeo(
            locations=labeled,
            locationmode="USA-states",
            mode="text",
            text=[f"<b>{s}</b><br>{big.loc[s, 'growth']:+.0f}%" for s in labeled],
            textfont=dict(
                size=10,
                color=[
                    "white"
                    if abs(big.loc[s, "growth"] - national) > span * 0.55
                    else BLACK
                    for s in labeled
                ],
            ),
            hoverinfo="skip",
            showlegend=False,
        )
    )
    if f.state in by_state.index:
        fig.add_trace(
            go.Choropleth(
                locations=[f.state],
                locationmode="USA-states",
                z=[1],
                colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
                showscale=False,
                marker_line_color=BLACK,
                marker_line_width=2.5,
                hoverinfo="skip",
                unselected=dict(marker=dict(opacity=1)),
            )
        )
    fig.update_geos(
        domain=dict(x=[0, 0.9]),
        scope="usa",
        projection_type="albers usa",
        showlakes=False,
        bgcolor="white",
        landcolor=FAINT,
    )
    base_theme(fig, height, margin=dict(l=0, r=0, t=0, b=0))
    return Chart(headline, caption, fig)


# 6. Which industries hold the largest and fastest-growing broker compensation pools?


def industries(t: Tables, f: Filters, height: int = 400, top_n: int = 12) -> Chart:
    df = subset(t.contracts, f, industry=False)
    df = df[(df["sector"] != "Unknown") & df["year"].isin([f.start, f.end])]
    industry = (
        df.assign(comp=df["commissions"] + df["fees"])
        .pivot_table(index="sector", columns="year", values="comp", aggfunc="sum")
        .reindex(columns=[f.start, f.end])
        .fillna(0)
    )
    industry = industry[(industry[f.start] > 0) & (industry[f.end] > 0)]
    if len(industry) < 3:
        return Chart(
            "Too few industries with broker pay for this selection",
            "",
            empty_figure("Too few industries", height),
        )

    industry["growth"] = growth(industry[f.end], industry[f.start])
    industry = industry.sort_values(f.end, ascending=False)
    largest = industry.index[0]
    fastest = industry.head(10)["growth"].idxmax()
    if fastest == largest:
        headline = f"{largest} is the largest and fastest-growing broker pay pool among the top 10"
    else:
        headline = _fit(
            f"{largest} is the largest broker pay pool; {fastest} is growing fastest among the top 10",
            f"{largest} is the largest pool; {fastest} is growing fastest",
            limit=118,
        )
    caption = (
        f"Broker pay in {f.end} for the {min(top_n, len(industry))} largest sponsor industries, shaded by "
        f"growth since {f.start}. Click an industry to filter."
    )

    shown = industry.head(top_n)
    if f.industry in industry.index and f.industry not in shown.index:
        shown = pd.concat([shown.iloc[:-1], industry.loc[[f.industry]]])
    shown = shown.iloc[::-1]  # largest on top
    lo, hi = min(0, industry["growth"].min()), industry["growth"].max()
    colors = [
        scale_color(g, lo, hi)
        if (not f.industry or s == f.industry)
        else fade(scale_color(g, lo, hi), 0.7)
        for s, g in zip(shown.index, shown["growth"])
    ]
    ticks = [f"<b>{s}</b>" if s == f.industry else s for s in shown.index]
    scale, suffix = _unit(shown[f.end].max())
    fig = go.Figure(
        go.Bar(
            y=ticks,
            x=shown[f.end] / scale,
            orientation="h",
            marker=dict(color=colors),
            text=[
                f"{money(v)}  {g:+.0f}%" for v, g in zip(shown[f.end], shown["growth"])
            ],
            textposition="outside",
            textfont=dict(size=11, color=BLACK),
            cliponaxis=False,
            customdata=shown.index,
            hovertemplate="<b>%{customdata}</b><br>"
            + str(f.end)
            + f" pool: {USD}%{{x:.2f}}{suffix}<extra></extra>",
            **KEEP_STYLE,
        )
    )
    base_theme(fig, height, margin=dict(l=10, r=10, t=10, b=10))
    fig.update_layout(
        bargap=0.25,
        xaxis=dict(visible=False, range=[0, shown[f.end].max() / scale * 1.35]),
        yaxis=dict(showgrid=False, tickfont=dict(size=11)),
    )
    return Chart(headline, caption, fig)


# 4. Is self-funding moving down-market into smaller employers?

YEAR_COLORS = ["#D9D9D9", "#C9E3A0", PALETTE[0], PALETTE[1], "#2E8B3A", PALETTE[2]]


def _band_rates(
    df: pd.DataFrame, bands: list[str], f: Filters, numerator: str
) -> pd.DataFrame:
    agg = df.groupby(["band", "year"])[[numerator, "plans"]].sum()
    agg = agg[
        agg["plans"] >= 25
    ]  # skip unstable cells when a filter leaves very few plans
    rates = (
        (agg[numerator] / agg["plans"] * 100)
        .unstack("year")
        .reindex(index=bands, columns=f.years)
    )
    return rates.dropna(subset=[f.start, f.end])


def self_funding(t: Tables, f: Filters, height: int = 300) -> Chart:
    notes: list[dict] = []
    rates = _band_rates(subset(t.health, f), SELF_FUNDING_BANDS, f, "self_funded")
    if len(rates) < 2:
        return Chart(
            "Too few health plans for this selection",
            "",
            empty_figure("Too few plans", height),
        )

    rates["delta"] = rates[f.end] - rates[f.start]
    lead = rates["delta"].idxmax()
    d = rates.loc[lead, "delta"]
    if d <= 0:
        headline = f"Self-funding is flat or falling in every plan size since {f.start}"
    elif lead in SELF_FUNDING_BANDS[:2]:
        headline = f"Self-funding is moving down-market: {lead}-participant plans are up {d:.1f} pts since {f.start}"
    else:
        headline = f"Self-funding grew most among {lead}-participant plans, up {d:.1f} pts since {f.start}"
    caption = (
        "Health plans (100+ participants) with no fully insured medical contract on Schedule A, "
        "meaning self-funded or level-funded."
    )

    bands = rates.index.tolist()
    colors = YEAR_COLORS[-len(f.years) :]
    fig = go.Figure()
    for band in bands:
        row = rates.loc[band, f.years].dropna()
        fig.add_trace(
            go.Scatter(
                x=[row.min(), row.max()],
                y=[band, band],
                mode="lines",
                line=dict(color="#E3E3E3", width=11),
                showlegend=False,
                hoverinfo="skip",
            )
        )
    for year, color in zip(f.years, colors):
        fig.add_trace(
            go.Scatter(
                x=rates[year],
                y=bands,
                mode="markers",
                name=str(year),
                marker=dict(
                    size=19 if year == f.end else 13,
                    color=color,
                    line=dict(color="white", width=1.5),
                ),
                hovertemplate=f"{year}<br>%{{y}} participants<br>%{{x:.1f}}% self-funded<extra></extra>",
            )
        )
    for band, delta in rates["delta"].items():
        notes.append(
            dict(
                x=rates.loc[band, f.years].max(),
                y=band,
                text=f"<b>{delta:+.1f} pts</b>",
                showarrow=False,
                xanchor="left",
                xshift=14,
                font=dict(size=12, color=trend_color(delta, 1)),
            )
        )
    x_min, x_max = np.nanmin(rates[f.years].values), np.nanmax(rates[f.years].values)
    base_theme(fig, height, margin=dict(l=10, r=10, t=26, b=10))
    fig.update_layout(
        legend=dict(y=1.0, yanchor="bottom", x=1, xanchor="right", font=dict(size=11)),
        xaxis=dict(
            ticksuffix="%",
            range=[np.floor(x_min / 5) * 5 - 2, np.ceil(x_max / 5) * 5 + 8],
            gridcolor=GRID,
            zeroline=False,
            tickfont=dict(size=11),
        ),
        yaxis=dict(
            categoryorder="array",
            categoryarray=bands[::-1],
            showgrid=False,
            tickfont=dict(size=11),
            title=dict(text="Participants", font=dict(size=11, color=GREY)),
        ),
    )
    fig.update_layout(annotations=notes)
    return Chart(headline, caption, fig)


# 8. Is voluntary benefits adoption spreading across employer sizes?

BAND_COLORS = ["#A9D46F", PALETTE[0], PALETTE[1], "#2E8B3A", PALETTE[2]]


def voluntary(t: Tables, f: Filters, height: int = 300) -> Chart:
    notes: list[dict] = []
    adoption = _band_rates(subset(t.voluntary, f), VOLUNTARY_BANDS, f, "with_voluntary")
    if len(adoption) < 2:
        return Chart(
            "Too few welfare plans for this selection",
            "",
            empty_figure("Too few plans", height),
        )

    adoption["delta"] = adoption[f.end] - adoption[f.start]
    lead = adoption["delta"].idxmax()
    up = (adoption["delta"] > 0).sum()
    if up == 0:
        headline = f"Voluntary benefits adoption has not grown in any plan size since {f.start}"
    else:
        scope = (
            "every"
            if up == len(adoption)
            else "most"
            if up > len(adoption) / 2
            else "some"
        )
        sizes = "plan size" if scope == "every" else "plan sizes"
        gain = f"+{adoption.loc[lead, 'delta']:.1f} pts"
        headline = _fit(
            f"Voluntary benefits adoption rose in {scope} {sizes}; "
            f"{lead}-participant plans gained the most ({gain})",
            f"Voluntary benefits adoption rose in {scope} {sizes}, led by {lead} participants ({gain})",
            limit=98,
        )
    caption = (
        "Plans (100+ participants) with an insured voluntary contract, such as accident or "
        "critical illness cover."
    )

    fig = go.Figure()
    color_for = dict(zip(VOLUNTARY_BANDS, BAND_COLORS))
    for band in adoption.index:
        y = adoption.loc[band, f.years]
        color = color_for[band]
        fig.add_trace(
            go.Scatter(
                x=f.years,
                y=y,
                mode="lines+markers",
                name=band,
                line=dict(color=color, width=3.5),
                marker=dict(
                    size=[8] + [5] * (len(f.years) - 2) + [11]
                    if len(f.years) > 1
                    else 10,
                    color=color,
                    line=dict(color="white", width=1.5),
                ),
                hovertemplate=f"{band} participants<br>%{{x}}: %{{y:.1f}}% of plans<extra></extra>",
                showlegend=False,
            )
        )
        notes.append(
            dict(
                x=f.end,
                y=y.iloc[-1],
                xanchor="left",
                xshift=12,
                showarrow=False,
                text=f"<b>{band}</b>  {y.iloc[-1]:.0f}%  ({adoption.loc[band, 'delta']:+.1f} pts)",
                font=dict(size=11, color=BLACK),
            )
        )
    vals = adoption[f.years].values
    base_theme(fig, height, margin=dict(l=10, r=200, t=10, b=10))
    fig.update_layout(
        xaxis=dict(
            tickvals=f.years,
            showgrid=False,
            range=[f.start - 0.2, f.end + 0.1],
            tickfont=dict(size=11),
        ),
        yaxis=dict(
            ticksuffix="%",
            gridcolor=GRID,
            zeroline=False,
            tickfont=dict(size=11),
            range=[
                np.floor(np.nanmin(vals) / 10) * 10 - 2,
                np.ceil(np.nanmax(vals) / 10) * 10 + 2,
            ],
        ),
    )
    fig.update_layout(annotations=notes)
    return Chart(headline, caption, fig)
