"""Fee adoption and take rate by line of coverage (analyses 3 and 7)."""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from figures.analyses.common import Chart, fit, line_name
from figures.data import Filters, Tables, subset
from figures.theme import (
    BLACK,
    GREEN_SCALE,
    GREY,
    MUTED,
    PALETTE,
    RED,
    base_theme,
    empty_figure,
    join_names,
    trend_color,
)

# 3. Is broker pay shifting from commissions toward carrier-paid fees?


def fee_adoption(
    t: Tables,
    f: Filters,
    focus: list[str] | None = None,
    height: int = 400,
    exclude_blank: bool = False,
) -> Chart:
    notes: list[dict] = []
    df = subset(t.contracts, f)
    df = df[df["line"] != "Unclassified"]
    agg = df.groupby(["line", "year"])[
        ["fee_contracts", "contracts", "blank_contracts"]
    ].sum()
    if exclude_blank:
        # Blank contracts never have fees, so only the contract count changes
        agg["contracts"] = agg["contracts"] - agg["blank_contracts"]
    agg = agg[agg["contracts"] >= 20]
    fee_mix = (agg["fee_contracts"] / agg["contracts"] * 100).unstack("year")
    fee_mix = fee_mix.reindex(columns=f.years).dropna(subset=[f.start, f.end])
    counts = (
        agg["contracts"].unstack("year").reindex(index=fee_mix.index, columns=f.years)
    )
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
        led = f"led by {line_name(lead)} (+{rising.loc[lead, 'delta']:.0f} pts)"
        headline = fit(
            f"Carrier-paid fees are spreading: up 2+ pts in {where} since {f.start}, {led}",
            f"Carrier-paid fees are up 2+ pts in {where}, {led}",
            limit=100,
        )
    else:
        headline = f"Carrier-paid fee adoption has not moved much since {f.start}"
    caption = "Contracts where the carrier paid the broker fees (bonuses, overrides, service fees), not just commissions."
    if exclude_blank:
        caption += " Contracts that left both pay amounts blank are left out."

    counts = counts.loc[fee_mix.index]
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
            customdata=counts.fillna(0).values,
            hovertemplate="%{y}<br>%{x}: %{z:.1f}% of %{customdata:,.0f} contracts<extra></extra>",
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
    t: Tables,
    f: Filters,
    focus: list[str] | None = None,
    height: int = 400,
    exclude_blank: bool = False,
) -> Chart:
    notes: list[dict] = []
    shapes: list[dict] = []
    df = subset(t.contracts, f)
    df = df[df["line"] != "Unclassified"]
    if exclude_blank:
        # Blank contracts have premium but no pay, so only premium changes
        df = df.assign(tr_premium=df["tr_premium"] - df["blank_tr_premium"])
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
    up = join_names([line_name(n) for n in rising[:2]])
    down = join_names([line_name(n) for n in falling[:2]])
    if len(falling) and len(rising):
        headline = fit(
            f"Take rates are compressing in {down} but climbing in {up}",
            f"Take rates are compressing in {line_name(falling[0])} but climbing in {up}",
            f"Take rates are compressing in {line_name(falling[0])} but climbing in {line_name(rising[0])}",
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
    if exclude_blank:
        caption += " Contracts that left both pay amounts blank are left out."

    # 3 panels per row so the labels are readable on a laptop
    n_cols = 3
    n_rows = int(np.ceil(len(rates) / n_cols))
    height += 45 * max(n_rows - 2, 0)
    fig = make_subplots(
        rows=n_rows,
        cols=n_cols,
        shared_yaxes=True,
        horizontal_spacing=0.04,
        vertical_spacing=0.42 / n_rows,
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
                # Change goes next to the name instead of the corner so they don't overlap
                # on narrow panels
                text=f"<b>{line}</b> <span style='color:{GREY if dim else color}'>"
                f"<b>{pct:+.0f}%</b></span><br>"
                f"{rates.loc[line, f.start]:.2f}% to {rates.loc[line, f.end]:.2f}%",
                showarrow=False,
                align="left",
                font=dict(size=11, color=GREY if dim else BLACK),
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
