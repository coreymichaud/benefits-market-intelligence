"""Broker firm stats, leaderboard and wins/losses (analyses 5 and 9)."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from figures.analyses.common import Chart, fit, nice_step
from figures.data import Filters, Tables, subset
from figures.theme import (
    ACCENT,
    BLACK,
    GREY,
    GRID,
    KEEP_STYLE,
    MUTED,
    PALETTE,
    RED,
    base_theme,
    empty_figure,
    fade,
    growth,
    join_names,
    trend_color,
)

# 5 & 9. Broker firms: plans served, ranks, wins and losses


def firm_stats(t: Tables, f: Filters) -> pd.DataFrame:
    """One row per firm with plans served and rank by year, plus wins and losses.

    A move between two years counts in the later year, same as the notebook.
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
    """Firms in the top 10 in the first or last year, same as the notebook's bump chart."""
    return stats[(stats["rank_first"] <= 10) | (stats["rank_last"] <= 10)]


GLOBAL_CONSULTANCIES = {"WTW", "Mercer", "Aon"}


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

        headline = fit(
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
            headline = fit(
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
    # Separate legend entries since the bar colors get faded when a firm is focused
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
    step = nice_step(x_min + x_max, 6)
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
